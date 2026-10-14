from django.urls import include, path

from common.health import healthz
from common.views import StatusView

urlpatterns = [
    # BE-API-10: liveness is routed outside the API framework.
    path("healthz", healthz),
    path("api/status/", StatusView.as_view()),
    path("api/invitations/", include("invitations.urls")),
    path("api/teams/", include("teams.urls")),
]
