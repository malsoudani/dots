from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.requests import parse_request
from teams.domains import SearchMembersRequest
from teams.service import TeamService


class TeamMembersView(APIView):
    def get(self, request: Request, team_id: str) -> Response:
        query = parse_request(SearchMembersRequest, request.query_params.dict())
        members = TeamService.factory().search_members(request.user.id, team_id, query.q)
        return Response(members.to_dict())
