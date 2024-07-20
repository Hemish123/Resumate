from django.urls import path
from . import views
from .views import CandidateCreateView, CandidateListView, CandidateDetailsView

urlpatterns = [
    path('', CandidateCreateView.as_view(), name='candidate-create'),
    path('candidate-list/', CandidateListView.as_view(), name='candidate-list'),
    path('candidate-details/<int:pk>/', CandidateDetailsView.as_view(), name='candidate-details'),
]