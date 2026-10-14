from django.urls import path

from invitations.views import InvitationsView, RevokeInvitationView

urlpatterns = [
    path("", InvitationsView.as_view()),
    path("<str:invitation_id>/revoke/", RevokeInvitationView.as_view()),
]
