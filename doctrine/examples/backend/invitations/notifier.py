import logging

from invitations.domains import InvitationDomain

logger = logging.getLogger(__name__)


class NotifierError(Exception):
    """The provider could not take the message. Raised instead of any provider SDK error."""


class Notifier:
    """What the invitation service needs from a mail provider.

    BE-EXT-2: a real implementation is the only module that imports the provider's
    SDK, and it raises NotifierError for every provider failure.
    """

    def send_invitation(self, invitation: InvitationDomain) -> None:
        raise NotImplementedError


class LoggingNotifier(Notifier):
    """Default wiring: logs instead of sending, so the example needs no provider."""

    def send_invitation(self, invitation: InvitationDomain) -> None:
        # The id is enough to trace a send; the address is personal data and stays out of logs.
        logger.info(
            "Invitation %s for team %s: notification logged, not sent",
            invitation.id,
            invitation.team_id,
        )
