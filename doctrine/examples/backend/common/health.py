from django.http import HttpRequest, JsonResponse


def healthz(request: HttpRequest) -> JsonResponse:
    """Liveness (BE-API-10): a plain view that touches no database and no dependency."""
    return JsonResponse({"status": "ok"})
