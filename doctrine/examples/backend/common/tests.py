import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from pydantic import Field
from rest_framework.test import APITestCase

from common.domains import RequestDomain
from common.exceptions import InvalidRequest
from common.requests import parse_request


class RenameRequest(RequestDomain):
    name: str = Field(min_length=1)
    size: int = 1


class HealthTests(TestCase):
    def test_healthz_answers_ok_with_zero_queries_and_no_credentials(self):
        with self.assertNumQueries(0):
            response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class PublicEndpointTests(APITestCase):
    def test_status_answers_without_credentials(self):
        response = self.client.get("/api/status/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_framework_error_uses_the_single_error_shape(self):
        response = self.client.post("/api/status/", {}, format="json")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {"error": "The request could not be processed."})


class ParseRequestTests(SimpleTestCase):
    def test_ignores_unknown_fields_and_strips_surrounding_whitespace(self):
        request = parse_request(RenameRequest, {"name": "  Ada  ", "color": "green"})

        self.assertEqual(request.model_dump(), {"name": "Ada", "size": 1})

    def test_whitespace_only_text_is_reported_as_required(self):
        with self.assertRaises(InvalidRequest) as raised:
            parse_request(RenameRequest, {"name": "   "})

        self.assertEqual(raised.exception.message, "name is required")
        self.assertEqual(raised.exception.status_code, 400)

    def test_non_object_body_is_rejected_with_the_contract_message(self):
        with self.assertRaises(InvalidRequest) as raised:
            parse_request(RenameRequest, ["name", "Ada"])

        self.assertEqual(raised.exception.message, "Request body must be a JSON object.")

    def test_unmapped_validation_failure_names_the_field_without_validator_jargon(self):
        with self.assertRaises(InvalidRequest) as raised:
            parse_request(RenameRequest, {"name": "Ada", "size": "large"})

        self.assertEqual(raised.exception.message, "size is invalid")


class StructureTests(SimpleTestCase):
    def test_domain_modules_load_without_django_or_any_models_module(self):
        # BE-STRUCT-2: a fresh interpreter proves the import direction, not a grep.
        probe = (
            "import sys, common.domains, teams.domains, invitations.domains;"
            "loaded = [name for name in sys.modules if name.startswith('django')];"
            "loaded += [name for name in sys.modules if name.endswith('.models')];"
            "print(loaded)"
        )

        result = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual(result.stdout.strip(), "[]")
