from django.urls import path
from . import views
from .views import (CandidateCreateView, CandidateListView,
                    CandidateDetailsView, CandidateUpdateView,
                    CandidateDeleteView, ApplicationSuccessView)

urlpatterns = [
    path('application-create/<int:pk>/', CandidateCreateView.as_view(), name='application_create'),
    path('candidate-list/', CandidateListView.as_view(), name='candidate-list'),
    path('candidate-details/<int:pk>/', CandidateDetailsView.as_view(), name='candidate-details'),
    path('candidate-update/<int:pk>/', CandidateUpdateView.as_view(), name='candidate-update'),
    path('candidate-delete/', CandidateDeleteView.as_view(), name='candidate-delete'),
    # path('application-create/<int:pk>/', ApplicationCreateView.as_view(), name='application_create'),
    path('application-success/<int:pk>/', ApplicationSuccessView.as_view(), name='application_success'),
]