from django.urls import path
from . import views
from .views import CandidateCreateView

urlpatterns = [
    path('', CandidateCreateView.as_view(), name='candidate-create'),


]