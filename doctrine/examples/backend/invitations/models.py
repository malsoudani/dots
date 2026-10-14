from django.conf import settings
from django.db import models

from common.models import BaseModel
from invitations.domains import InvitationStatus


class Invitation(BaseModel):
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    role = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default=InvitationStatus.PENDING.value)
    message = models.CharField(max_length=500, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # BE-DB-3: "one invitation per email per team" is decided by the database, not by a lookup.
        constraints = [
            models.UniqueConstraint(
                fields=["team", "email"], name="unique_invitation_per_team_email"
            ),
        ]


class InvitationEvent(BaseModel):
    """Audit trail: who did what to an invitation, written in the same transaction as the change."""

    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name="events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    action = models.CharField(max_length=20)
