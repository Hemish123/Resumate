from django.urls import path
from . import views
from .views import CandidateCreateView, CandidateListView, CandidateDetailsView, CandidateUpdateView, CandidateDeleteView

urlpatterns = [
    path('', CandidateCreateView.as_view(), name='candidate-create'),
    path('candidate-list/', CandidateListView.as_view(), name='candidate-list'),
    path('candidate-details/<int:pk>/', CandidateDetailsView.as_view(), name='candidate-details'),
    path('candidate-update/<int:pk>/', CandidateUpdateView.as_view(), name='candidate-update'),
    path('candidate-delete/', CandidateDeleteView.as_view(), name='candidate-delete'),
]