from django.urls import path
from . import views
from .views import (CandidateCreateView, CandidateListView,
                    CandidateDetailsView, CandidateUpdateView, CandidateImportView,
                    CandidateDeleteView, ApplicationSuccessView, ResumeListView, ResumeSearchView,
                    CandidateAnalysisView, ApplicationListView)

urlpatterns = [
    path('application-create/<int:pk>/', CandidateCreateView.as_view(), name='application_create'),
    path('candidate-list/', CandidateListView.as_view(), name='candidate-list'),
    path('add-candidate-form/', CandidateImportView.as_view(), name='candidate-import'),
    path('resume-list/', ResumeListView.as_view(), name='resume-list'),
    path('resume-search/', ResumeSearchView.as_view(), name='resume-search'),
    path('candidate-details/<int:pk>/', CandidateDetailsView.as_view(), name='candidate-details'),
    path('candidate-update/<int:pk>/', CandidateUpdateView.as_view(), name='candidate-update'),
    path('candidate-delete/', CandidateDeleteView.as_view(), name='candidate-delete'),
    # path('application-create/<int:pk>/', ApplicationCreateView.as_view(), name='application_create'),
    path('application-success/<int:pk1>/<int:pk2>/', ApplicationSuccessView.as_view(), name='application_success'),
    path('candidate-analysis/<int:pk>/', CandidateAnalysisView.as_view(), name='candidate-analysis'),
    path('application-list/<int:pk>/', ApplicationListView.as_view(), name='application-list'),

]