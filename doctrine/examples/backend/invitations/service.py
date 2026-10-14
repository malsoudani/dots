import logging
from functools import partial

from django.db import IntegrityError, transaction

from common.exceptions import BusinessError
from invitations.domains import (
    CreateInvitationRequest,
    InvitationAction,
    InvitationDomain,
    InvitationListDomain,
    InvitationStatus,
)
from invitations.models import Invitation, InvitationEvent
from invitations.notifier import LoggingNotifier, Notifier, NotifierError
from teams.service import TeamService

logger = logging.getLogger(__name__)


class InvitationNotFound(BusinessError):
    status_code = 404

    def __init__(self, invitation_id: str) -> None:
        super().__init__(f"Invitation {invitation_id} was not found.")


class InvalidInvitationState(BusinessError):
    """The invitation is not in a state that allows the requested change."""


class InvitationService:
    def __init__(self, team_service: TeamService, notifier: Notifier) -> None:
        self._team_service = team_service
        self._notifier = notifier

    @classmethod
    def factory(cls) -> "InvitationService":
        return cls(TeamService.factory(), LoggingNotifier())

    def list_invitations(self, actor_id: str, team_id: str) -> InvitationListDomain:
        # BE-SVC-3: membership is the team slice's rule, so its service decides.
        self._team_service.require_member(actor_id, team_id)
        return self._snapshot(team_id)

    @transaction.atomic
    def create_invitation(
        self, actor_id: str, request: CreateInvitationRequest
    ) -> InvitationListDomain:
        self._team_service.require_member(actor_id, request.team_id)
        # BE-SVC-6: a resubmitted invitation is the same invitation, not a second one.
        if not self._is_invited(request.team_id, request.email):
            self._invite(actor_id, request)
        return self._snapshot(request.team_id)

    @transaction.atomic
    def revoke_invitation(self, actor_id: str, invitation_id: str) -> InvitationListDomain:
        invitation = Invitation.objects.filter(id=invitation_id).first()
        # BE-API-6: an invitation in someone else's team looks exactly like one that does not exist.
        if invitation is None or not self._team_service.is_member(actor_id, invitation.team_id):
            raise InvitationNotFound(invitation_id)
        if invitation.status != InvitationStatus.PENDING:
            raise InvalidInvitationState("Only a pending invitation can be revoked.")
        invitation.status = InvitationStatus.REVOKED.value
        invitation.save(update_fields=["status", "updated_at"])
        self._record(invitation, actor_id, InvitationAction.REVOKED)
        return self._snapshot(invitation.team_id)

    def _is_invited(self, team_id: str, email: str) -> bool:
        return Invitation.objects.filter(team_id=team_id, email=email).exists()

    def _invite(self, actor_id: str, request: CreateInvitationRequest) -> None:
        try:
            # BE-TXN-3: the savepoint keeps the outer transaction usable. Without it the
            # failed INSERT poisons the transaction and the snapshot query raises.
            with transaction.atomic():
                invitation = Invitation.objects.create(
                    team_id=request.team_id,
                    email=request.email,
                    role=request.role.value,
                    message=request.message or "",
                    expires_at=request.expires_at,
                )
        except IntegrityError:
            # BE-DB-3: a concurrent request inserted the same (team, email) first.
            # Its row is the result, exactly as if the lookup had found it.
            return
        self._record(invitation, actor_id, InvitationAction.CREATED)
        # BE-TXN-4: the notification cannot be rolled back, so it is sent only once the
        # invitation is committed. BE-TXN-2: by then no transaction is open.
        transaction.on_commit(partial(self._notify, InvitationDomain.from_model(invitation)))

    def _notify(self, invitation: InvitationDomain) -> None:
        try:
            self._notifier.send_invitation(invitation)
        except NotifierError:
            # The invitation is already committed: log the failed send and let the request succeed.
            logger.exception("Invitation %s was saved but its notification failed", invitation.id)

    def _record(self, invitation: Invitation, actor_id: str, action: InvitationAction) -> None:
        InvitationEvent.objects.create(
            invitation=invitation, actor_id=actor_id, action=action.value
        )

    def _snapshot(self, team_id: str) -> InvitationListDomain:
        # CT-5: the read and both writes answer with this one shape.
        rows = Invitation.objects.filter(team_id=team_id).order_by("created_at", "id")
        invitations = [InvitationDomain.from_model(row) for row in rows]
        return InvitationListDomain(team_id=team_id, invitations=invitations)
