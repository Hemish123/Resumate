from django.urls import path
from . import views
from .views import JobOpeningView, StageView,StageAPIView, CandidateAPIView, CalendarView, HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='dashboard'),
    path('job-openings/', JobOpeningView.as_view(), name='job-opening'),
    path('job-process/<int:pk>/', StageView.as_view(), name='job-process'),
    path('stage-api/<int:pk>/', StageAPIView.as_view(), name='stage-api'),
    path('candidate-api/', CandidateAPIView.as_view(), name='candidate-api'),
    path('calendar/', CalendarView.as_view(), name='calendar')

]


