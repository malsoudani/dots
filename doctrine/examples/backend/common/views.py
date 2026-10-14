from typing import Optional

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler

from common.exceptions import BusinessError

# BE-API-3, BE-API-4: framework errors get fixed sentences; framework detail never reaches a client.
FRAMEWORK_MESSAGES = {
    400: "Request body must be a JSON object.",
    401: "Sign in to continue.",
}
FALLBACK_MESSAGE = "The request could not be processed."


def api_exception_handler(exc: Exception, context: dict) -> Optional[Response]:
    """BE-API-2: the one place that builds an error body."""
    if isinstance(exc, BusinessError):
        return Response({"error": exc.message}, status=exc.status_code)
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {"error": FRAMEWORK_MESSAGES.get(response.status_code, FALLBACK_MESSAGE)}
    # None means a bug: it stays an exception and becomes a 500.
    return response


class PublicAPIView(APIView):
    """BE-API-5: the only way to be public. Every other view inherits the authenticated default."""

    authentication_classes = []
    permission_classes = []


class StatusView(PublicAPIView):
    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})
