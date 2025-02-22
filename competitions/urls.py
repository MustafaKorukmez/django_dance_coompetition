from django.urls import path
from .views import final_results_view

urlpatterns = [
    path('competition/<int:competition_id>/final-results/', final_results_view, name='final_results'),
]
