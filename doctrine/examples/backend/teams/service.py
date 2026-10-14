from django.db.models import Q

from common.exceptions import BusinessError
from teams.domains import MemberDomain, TeamMembersDomain
from teams.models import Membership


class TeamNotFound(BusinessError):
    status_code = 404

    def __init__(self, team_id: str) -> None:
        super().__init__(f"Team {team_id} was not found.")


class TeamService:
    @classmethod
    def factory(cls) -> "TeamService":
        return cls()

    def is_member(self, user_id: str, team_id: str) -> bool:
        return Membership.objects.filter(team_id=team_id, user_id=user_id).exists()

    def require_member(self, user_id: str, team_id: str) -> None:
        # BE-API-6: a team the caller is not in looks exactly like a team that does not exist.
        if not self.is_member(user_id, team_id):
            raise TeamNotFound(team_id)

    def search_members(self, actor_id: str, team_id: str, query: str) -> TeamMembersDomain:
        self.require_member(actor_id, team_id)
        memberships = Membership.objects.filter(team_id=team_id).select_related("user")
        if query:
            matches = Q(user__name__icontains=query) | Q(user__email__icontains=query)
            memberships = memberships.filter(matches)
        rows = memberships.order_by("user__name", "user__id")
        return TeamMembersDomain(
            team_id=team_id, members=[MemberDomain.from_model(row.user) for row in rows]
        )
