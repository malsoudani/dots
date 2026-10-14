from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Optional

from pydantic import AfterValidator, AwareDatetime, EmailStr, Field

from common.domains import RequestDomain, ResponseDomain

if TYPE_CHECKING:  # BE-STRUCT-2: models are a type-only import here.
    from invitations.models import Invitation


class Role(str, Enum):
    MEMBER = "member"
    ADMIN = "admin"


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"


class InvitationAction(str, Enum):
    CREATED = "created"
    REVOKED = "revoked"


class ListInvitationsRequest(RequestDomain):
    team_id: str = Field(min_length=1)


class CreateInvitationRequest(RequestDomain):
    team_id: str = Field(min_length=1)
    # Lowercased so the (team, email) natural key does not depend on letter case (BE-SVC-6).
    email: Annotated[EmailStr, AfterValidator(str.lower)]
    role: Role
    # CT-3: null and absent mean the same. BE-API-7: reject over the cap, never truncate.
    message: Optional[str] = Field(default=None, max_length=500)
    # BE-API-8: a timestamp without an offset is rejected.
    expires_at: Optional[AwareDatetime] = None


class InvitationDomain(ResponseDomain):
    id: str
    team_id: str
    email: str
    role: str
    status: str
    message: str
    expires_at: Optional[datetime]
    created_at: datetime

    @classmethod
    def from_model(cls, row: "Invitation") -> "InvitationDomain":
        return cls(
            id=row.id,
            team_id=row.team_id,
            email=row.email,
            role=row.role,
            status=row.status,
            message=row.message,
            expires_at=row.expires_at,
            created_at=row.created_at,
        )


class InvitationListDomain(ResponseDomain):
    team_id: str
    invitations: list[InvitationDomain]
