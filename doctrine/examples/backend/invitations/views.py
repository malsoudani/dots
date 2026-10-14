from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.requests import parse_request
from invitations.domains import CreateInvitationRequest, ListInvitationsRequest
from invitations.service import InvitationService


class InvitationsView(APIView):
    def get(self, request: Request) -> Response:
        query = parse_request(ListInvitationsRequest, request.query_params.dict())
        snapshot = InvitationService.factory().list_invitations(request.user.id, query.team_id)
        return Response(snapshot.to_dict())

    def post(self, request: Request) -> Response:
        body = parse_request(CreateInvitationRequest, request.data)
        snapshot = InvitationService.factory().create_invitation(request.user.id, body)
        return Response(snapshot.to_dict())


class RevokeInvitationView(APIView):
    def post(self, request: Request, invitation_id: str) -> Response:
        snapshot = InvitationService.factory().revoke_invitation(request.user.id, invitation_id)
        return Response(snapshot.to_dict())
