from django.urls import path
from . import views
from .views import CandidateCreateView, CandidateListView

urlpatterns = [
    path('', CandidateCreateView.as_view(), name='candidate-create'),
    path('candidate-list/', CandidateListView.as_view(), name='candidate-list'),


]