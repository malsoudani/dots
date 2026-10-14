from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import User
from teams.models import Membership, Team


class TeamMembersTests(APITestCase):
    def setUp(self):
        self.ada = User.objects.create(email="ada@example.com", name="Ada Quill")
        self.ben = User.objects.create(email="ben@example.com", name="Ben Marsh")
        self.team = Team.objects.create(name="Platform")
        Membership.objects.create(team=self.team, user=self.ada)
        Membership.objects.create(team=self.team, user=self.ben)
        self.foreign_team = Team.objects.create(name="Billing")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {Token.objects.create(user=self.ada).key}"
        )

    def members_url(self, team_id):
        return f"/api/teams/{team_id}/members/"

    def test_members_returns_the_team_id_and_every_member_ordered_by_name(self):
        response = self.client.get(self.members_url(self.team.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "team_id": self.team.id,
                "members": [
                    {"id": self.ada.id, "email": "ada@example.com", "name": "Ada Quill"},
                    {"id": self.ben.id, "email": "ben@example.com", "name": "Ben Marsh"},
                ],
            },
        )

    def test_members_query_matches_name_or_email_ignoring_case(self):
        by_name = self.client.get(self.members_url(self.team.id), {"q": "MARSH"})
        by_email = self.client.get(self.members_url(self.team.id), {"q": "ada@"})

        self.assertEqual([member["id"] for member in by_name.json()["members"]], [self.ben.id])
        self.assertEqual([member["id"] for member in by_email.json()["members"]], [self.ada.id])

    def test_foreign_team_and_unknown_team_both_answer_404_with_the_same_message_shape(self):
        foreign = self.client.get(self.members_url(self.foreign_team.id))
        unknown = self.client.get(self.members_url("no-such-team"))

        self.assertEqual(foreign.status_code, 404)
        self.assertEqual(foreign.json(), {"error": f"Team {self.foreign_team.id} was not found."})
        self.assertEqual(unknown.status_code, 404)
        self.assertEqual(unknown.json(), {"error": "Team no-such-team was not found."})

    def test_query_of_100_characters_is_accepted_and_101_is_rejected(self):
        at_limit = self.client.get(self.members_url(self.team.id), {"q": "a" * 100})
        over_limit = self.client.get(self.members_url(self.team.id), {"q": "a" * 101})

        self.assertEqual(at_limit.status_code, 200)
        self.assertEqual(over_limit.status_code, 400)
        self.assertEqual(over_limit.json(), {"error": "q must be at most 100 characters"})

    def test_rows_get_distinct_opaque_string_ids_and_both_timestamps(self):
        self.assertIsInstance(self.team.id, str)
        self.assertFalse(self.team.id.isdigit())
        self.assertNotEqual(self.team.id, self.foreign_team.id)
        self.assertIsNotNone(self.team.created_at)
        self.assertIsNotNone(self.team.updated_at)
