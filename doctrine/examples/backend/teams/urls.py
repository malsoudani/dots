from django.urls import path

from teams.views import TeamMembersView

urlpatterns = [
    path("<str:team_id>/members/", TeamMembersView.as_view()),
]
