from django.urls import path
from .views import CreateScoreView, GroupRankParticipantsView, ActiveCompetitionsListView ,GroupParticipantsListView,CompetitionRoundsListView,  GroupBulkVotingView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/scores/', CreateScoreView.as_view(), name='create_score'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/groups/<int:group_id>/participants/', GroupParticipantsListView.as_view(), name='group-participants-list'),
    path('api/groups/<int:group_id>/rank/', GroupRankParticipantsView.as_view(), name='group-rank-participants'),
    path('api/groups/<int:group_id>/bulk-vote/', GroupBulkVotingView.as_view(), name='group_bulk_voting'),
    path('api/competitions/<int:competition_id>/rounds/', CompetitionRoundsListView.as_view(), name='competition_rounds_list'),
    path('api/competitions/active/', ActiveCompetitionsListView.as_view(), name='active_competitions'),

]
