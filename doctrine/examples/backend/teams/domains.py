from typing import TYPE_CHECKING

from pydantic import Field

from common.domains import RequestDomain, ResponseDomain

if TYPE_CHECKING:  # BE-STRUCT-2: models are a type-only import here.
    from accounts.models import User


class SearchMembersRequest(RequestDomain):
    q: str = Field(default="", max_length=100)


class MemberDomain(ResponseDomain):
    id: str
    email: str
    name: str

    @classmethod
    def from_model(cls, user: "User") -> "MemberDomain":
        return cls(id=user.id, email=user.email, name=user.name)


class TeamMembersDomain(ResponseDomain):
    team_id: str
    members: list[MemberDomain]
