from datetime import datetime, timezone
from unittest import mock

from django.db import connection
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APITransactionTestCase

from accounts.models import User
from invitations.models import Invitation, InvitationEvent
from invitations.notifier import Notifier, NotifierError
from invitations.service import InvitationService
from teams.models import Membership, Team
from teams.service import TeamService

URL = "/api/invitations/"
OFFSET_REQUIRED = "expires_at must be an ISO-8601 datetime with a timezone offset"


class InvitationScenario:
    """Ada belongs to `team`; `foreign_team` exists and she does not belong to it."""

    def setUp(self):
        self.ada = User.objects.create(email="ada@example.com", name="Ada Quill")
        self.team = Team.objects.create(name="Platform")
        Membership.objects.create(team=self.team, user=self.ada)
        self.foreign_team = Team.objects.create(name="Billing")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {Token.objects.create(user=self.ada).key}"
        )

    def invite(self, **changes):
        body = {"team_id": self.team.id, "email": "new@example.com", "role": "member", **changes}
        return self.client.post(URL, body, format="json")

    def revoke(self, invitation_id):
        return self.client.post(f"{URL}{invitation_id}/revoke/")

    def audit_store_down(self):
        return mock.patch.object(
            InvitationEvent.objects, "create", side_effect=RuntimeError("audit store down")
        )


class AuthenticationTests(InvitationScenario, APITestCase):
    def test_request_without_credentials_gets_401_in_the_error_shape(self):
        self.client.credentials()

        response = self.client.get(URL, {"team_id": self.team.id})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "Sign in to continue."})
        self.assertEqual(response["WWW-Authenticate"], "Bearer")


class ListInvitationsTests(InvitationScenario, APITestCase):
    def test_list_returns_the_team_id_and_every_invitation_field(self):
        row = Invitation.objects.create(
            team=self.team, email="new@example.com", role="admin", message="Welcome"
        )

        response = self.client.get(URL, {"team_id": self.team.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "team_id": self.team.id,
                "invitations": [
                    {
                        "id": row.id,
                        "team_id": self.team.id,
                        "email": "new@example.com",
                        "role": "admin",
                        "status": "pending",
                        "message": "Welcome",
                        "expires_at": None,
                        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
                    }
                ],
            },
        )

    def test_list_without_team_id_gets_400_team_id_is_required(self):
        response = self.client.get(URL)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "team_id is required"})

    def test_list_for_a_foreign_team_gets_the_same_404_as_an_unknown_team(self):
        Invitation.objects.create(team=self.foreign_team, email="new@example.com", role="member")

        foreign = self.client.get(URL, {"team_id": self.foreign_team.id})
        unknown = self.client.get(URL, {"team_id": "no-such-team"})

        self.assertEqual(foreign.status_code, 404)
        self.assertEqual(foreign.json(), {"error": f"Team {self.foreign_team.id} was not found."})
        self.assertEqual(unknown.status_code, 404)
        self.assertEqual(unknown.json(), {"error": "Team no-such-team was not found."})

    def test_list_serializes_a_stored_row_that_todays_input_rules_would_reject(self):
        Invitation.objects.create(team=self.team, email="root@localhost", role="owner")

        response = self.client.get(URL, {"team_id": self.team.id})

        self.assertEqual(response.status_code, 200)
        [invitation] = response.json()["invitations"]
        self.assertEqual((invitation["email"], invitation["role"]), ("root@localhost", "owner"))


class CreateInvitationTests(InvitationScenario, APITestCase):
    def test_create_answers_200_with_the_same_snapshot_the_list_endpoint_returns(self):
        created = self.invite()
        listed = self.client.get(URL, {"team_id": self.team.id})

        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.json(), listed.json())
        [invitation] = created.json()["invitations"]
        self.assertEqual(
            (invitation["email"], invitation["status"]), ("new@example.com", "pending")
        )

    def test_create_stores_one_pending_invitation_and_one_created_event_by_the_caller(self):
        self.invite(role="admin", message="Welcome")

        row = Invitation.objects.get()
        self.assertEqual(
            (row.team_id, row.email, row.role, row.status, row.message),
            (self.team.id, "new@example.com", "admin", "pending", "Welcome"),
        )
        event = InvitationEvent.objects.get()
        self.assertEqual(
            (event.invitation_id, event.actor_id, event.action), (row.id, self.ada.id, "created")
        )

    def test_create_treats_null_optionals_the_same_as_absent_ones(self):
        response = self.invite(message=None, expires_at=None)

        self.assertEqual(response.status_code, 200)
        row = Invitation.objects.get()
        self.assertEqual((row.message, row.expires_at), ("", None))

    def test_create_stores_expires_at_in_utc_and_returns_it_with_an_offset(self):
        response = self.invite(expires_at="2030-01-01T12:00:00+02:00")

        self.assertEqual(
            Invitation.objects.get().expires_at, datetime(2030, 1, 1, 10, tzinfo=timezone.utc)
        )
        self.assertEqual(response.json()["invitations"][0]["expires_at"], "2030-01-01T10:00:00Z")

    def test_each_invalid_field_gets_its_contract_message_and_nothing_is_stored(self):
        valid = {"team_id": self.team.id, "email": "new@example.com", "role": "member"}
        cases = [
            ({"team_id": self.team.id, "role": "member"}, "email is required"),
            ({**valid, "email": None}, "email is required"),
            ({**valid, "email": "   "}, "email is required"),
            ({**valid, "email": "not-an-address"}, "Enter a valid email address"),
            ({**valid, "role": "owner"}, "Unsupported role: owner"),
            ({**valid, "team_id": ""}, "team_id is required"),
            ({**valid, "expires_at": "2030-01-01T12:00:00"}, OFFSET_REQUIRED),
            ({**valid, "expires_at": "next week"}, OFFSET_REQUIRED),
            ({**valid, "expires_at": ""}, OFFSET_REQUIRED),
            (["team_id", self.team.id], "Request body must be a JSON object."),
        ]

        for body, message in cases:
            with self.subTest(message=message, body=body):
                response = self.client.post(URL, body, format="json")

                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {"error": message})
        self.assertEqual(Invitation.objects.count(), 0)

    def test_several_invalid_fields_are_reported_together_in_field_order(self):
        response = self.client.post(URL, {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"error": "team_id is required; email is required; role is required"}
        )

    def test_malformed_json_gets_400_in_the_error_shape(self):
        response = self.client.post(URL, "{not json", content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Request body must be a JSON object."})

    def test_message_of_500_characters_is_accepted_and_501_is_rejected(self):
        over_limit = self.invite(message="m" * 501)
        at_limit = self.invite(message="m" * 500)

        self.assertEqual(over_limit.status_code, 400)
        self.assertEqual(over_limit.json(), {"error": "message must be at most 500 characters"})
        self.assertEqual(at_limit.status_code, 200)
        self.assertEqual(len(Invitation.objects.get().message), 500)

    def test_create_for_a_foreign_team_gets_404_and_stores_nothing(self):
        response = self.invite(team_id=self.foreign_team.id)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": f"Team {self.foreign_team.id} was not found."})
        self.assertEqual(Invitation.objects.count(), 0)

    def test_submitting_twice_returns_equal_snapshots_and_keeps_one_row_and_one_event(self):
        first = self.invite()
        second = self.invite()

        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json(), first.json())
        self.assertEqual(Invitation.objects.count(), 1)
        self.assertEqual(InvitationEvent.objects.count(), 1)

    def test_same_email_in_another_letter_case_is_the_same_invitation(self):
        self.invite(email="New@Example.COM")
        self.invite(email="new@example.com")

        self.assertEqual([row.email for row in Invitation.objects.all()], ["new@example.com"])

    def test_losing_the_insert_race_answers_200_with_the_competitors_invitation(self):
        real_lookup = InvitationService._is_invited

        def lookup_then_competitor_inserts(service, team_id, email):
            # T-3: the competing row lands between our lookup and our insert. The lookup
            # is the only seam at that point, so this test reaches into the service.
            invited = real_lookup(service, team_id, email)
            Invitation.objects.create(team_id=team_id, email=email, role="admin")
            return invited

        with mock.patch.object(
            InvitationService,
            "_is_invited",
            autospec=True,
            side_effect=lookup_then_competitor_inserts,
        ):
            response = self.invite(role="member")

        self.assertEqual(response.status_code, 200)
        [invitation] = response.json()["invitations"]
        self.assertEqual(invitation["role"], "admin")
        self.assertEqual(Invitation.objects.count(), 1)

    def test_create_stores_nothing_when_the_audit_write_fails(self):
        with self.audit_store_down(), self.assertRaises(RuntimeError):
            self.invite()

        self.assertEqual(Invitation.objects.count(), 0)


class RevokeInvitationTests(InvitationScenario, APITestCase):
    def test_revoke_marks_the_invitation_revoked_records_an_event_and_returns_the_snapshot(self):
        row = Invitation.objects.create(team=self.team, email="new@example.com", role="member")

        response = self.revoke(row.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.client.get(URL, {"team_id": self.team.id}).json())
        self.assertEqual(response.json()["invitations"][0]["status"], "revoked")
        event = InvitationEvent.objects.get()
        self.assertEqual(
            (event.invitation_id, event.actor_id, event.action), (row.id, self.ada.id, "revoked")
        )

    def test_revoking_a_non_pending_invitation_gets_400_and_changes_nothing(self):
        row = Invitation.objects.create(
            team=self.team, email="new@example.com", role="member", status="accepted"
        )

        response = self.revoke(row.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Only a pending invitation can be revoked."})
        self.assertEqual(Invitation.objects.get().status, "accepted")
        self.assertEqual(InvitationEvent.objects.count(), 0)

    def test_foreign_invitation_gets_the_same_404_as_an_unknown_one_and_stays_pending(self):
        row = Invitation.objects.create(
            team=self.foreign_team, email="new@example.com", role="member"
        )

        foreign = self.revoke(row.id)
        unknown = self.revoke("no-such-invitation")

        self.assertEqual(foreign.status_code, 404)
        self.assertEqual(foreign.json(), {"error": f"Invitation {row.id} was not found."})
        self.assertEqual(unknown.status_code, 404)
        self.assertEqual(unknown.json(), {"error": "Invitation no-such-invitation was not found."})
        self.assertEqual(Invitation.objects.get().status, "pending")

    def test_revoke_leaves_the_invitation_pending_when_the_audit_write_fails(self):
        row = Invitation.objects.create(team=self.team, email="new@example.com", role="member")

        with self.audit_store_down(), self.assertRaises(RuntimeError):
            self.revoke(row.id)

        self.assertEqual(Invitation.objects.get().status, "pending")


class NotificationTests(InvitationScenario, APITransactionTestCase):
    """Real commits (no wrapping test transaction), so after-commit behavior is observable."""

    def setUp(self):
        super().setUp()
        # T-4: the fake is bound to the real signature and records every call.
        self.notifier = mock.create_autospec(Notifier, instance=True)
        service = InvitationService(TeamService.factory(), self.notifier)
        factory = mock.patch.object(InvitationService, "factory", return_value=service)
        factory.start()
        self.addCleanup(factory.stop)

    def test_notifier_runs_once_after_commit_and_outside_any_transaction(self):
        seen = []
        self.notifier.send_invitation.side_effect = lambda invitation: seen.append(
            (connection.in_atomic_block, Invitation.objects.filter(id=invitation.id).exists())
        )

        self.invite()

        self.notifier.send_invitation.assert_called_once()
        self.assertEqual(seen, [(False, True)])

    def test_notifier_is_never_called_when_the_transaction_rolls_back(self):
        with self.audit_store_down(), self.assertRaises(RuntimeError):
            self.invite()

        self.notifier.send_invitation.assert_not_called()
        self.assertEqual(Invitation.objects.count(), 0)

    def test_notifier_failure_after_commit_still_answers_200_and_keeps_the_invitation(self):
        self.notifier.send_invitation.side_effect = NotifierError("provider unavailable")

        with self.assertLogs("invitations.service", level="ERROR"):
            response = self.invite()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Invitation.objects.count(), 1)


class DefaultWiringTests(InvitationScenario, APITransactionTestCase):
    def test_factory_built_service_logs_the_invitation_id_and_never_the_email(self):
        with self.assertLogs("invitations.notifier", level="INFO") as logs:
            self.invite()

        [line] = logs.output
        self.assertIn(Invitation.objects.get().id, line)
        self.assertNotIn("new@example.com", line)


class CollaboratorTests(InvitationScenario, APITestCase):
    def test_membership_is_decided_by_the_team_service_and_not_by_the_invitations_slice(self):
        team_service = mock.create_autospec(TeamService, instance=True)
        service = InvitationService(team_service, mock.create_autospec(Notifier, instance=True))

        snapshot = service.list_invitations("not-a-member", self.foreign_team.id)

        team_service.require_member.assert_called_once_with("not-a-member", self.foreign_team.id)
        self.assertEqual(snapshot.to_dict(), {"team_id": self.foreign_team.id, "invitations": []})
