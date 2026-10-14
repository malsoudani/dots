from django.conf import settings
from django.db import models

from common.models import BaseModel


class Team(BaseModel):
    name = models.CharField(max_length=200)


class Membership(BaseModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "user"], name="unique_membership_per_team_user"
            ),
        ]
