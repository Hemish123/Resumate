from django.urls import path
from . import views
from .views import DashbaordView, StageView,StageAPIView, CandidateAPIView, CalendarView, HomeView


urlpatterns = [
    path('dashboard/', HomeView.as_view(), name='home'),
    path('', DashbaordView.as_view(), name='dashboard'),
    path('job-process/<int:pk>/', StageView.as_view(), name='job-process'),
    path('stage-api/<int:pk>/', StageAPIView.as_view(), name='stage-api'),
    path('candidate-api/', CandidateAPIView.as_view(), name='candidate-api'),
    path('calendar/', CalendarView.as_view(), name='calendar')

]


