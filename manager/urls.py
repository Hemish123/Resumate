from .views import (JobOpeningCreateView, ClientCreateView,
                    JobOpeningUpdateView, JobOpeningDeleteView,
                    )
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('job-opening-create/', JobOpeningCreateView.as_view(), name='job-opening'),
    path('create-client/', ClientCreateView.as_view(), name='create-client'),
    path('job-opening-update/<int:pk>/', JobOpeningUpdateView.as_view(), name='job-opening-update'),
    path('job-opening-delete/<int:pk>/', JobOpeningDeleteView.as_view(), name='job-opening-delete'),

]
