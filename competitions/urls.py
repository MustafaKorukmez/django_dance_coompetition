from django.urls import path
from .views import SplitContestantsIntoGroupsAPIView, RankGroupAPIView, CompleteStageAPIView

urlpatterns = [
    path('api/split-groups/', SplitContestantsIntoGroupsAPIView.as_view(), name='split-groups'),
    path('api/rank-group/', RankGroupAPIView.as_view(), name='rank-group'),
    path('api/complete-stage/', CompleteStageAPIView.as_view(), name='complete-stage'),

]
