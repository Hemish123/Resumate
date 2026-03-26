from django.urls import path
from . import views
from .views import (JobOpeningView, StageView,StageAPIView, CandidateAPIView, CalendarView, HomeView,
                    email_action, CandidateCalendarListView,SendInterviewLinkView, get_client_emails)


urlpatterns = [
    path('dashboard/', HomeView.as_view(), name='dashboard'),
    path('job-openings/', JobOpeningView.as_view(), name='job-opening'),
    path('job-process/<int:pk>/', StageView.as_view(), name='job-process'),
    path('stage-api/<int:pk>/', StageAPIView.as_view(), name='stage-api'),
    path('candidate-api/', CandidateAPIView.as_view(), name='candidate-api'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path("candidate/action/<int:candidate_id>/<str:action>/", email_action,name="process_candidate_action"),
    path('ajax/candidates/', CandidateCalendarListView.as_view(), name='ajax-candidates'),
    path('api/send-interview-link/', SendInterviewLinkView.as_view(), name='send_interview_link'),
    path('client-emails/<int:job_opening_id>/', views.get_client_emails, name='client-emails'),
    path('', views.landing_page, name="landing_page"),
    path('download-stage-csv/<int:job_opening_id>/', views.download_stage_csv, name='download-stage-csv'),
    


]


