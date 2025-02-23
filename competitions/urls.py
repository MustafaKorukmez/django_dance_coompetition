from django.urls import path
from .views import CreateScoreView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/scores/', CreateScoreView.as_view(), name='create_score'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
