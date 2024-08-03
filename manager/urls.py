from .views import JobOpeningCreateView, OrganizationCreateView, JobOpeningUpdateView, JobOpeningDeleteView, ApplicationCreateView,ApplicationSuccessView
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('job-opening-create/', JobOpeningCreateView.as_view(), name='job-opening'),
    path('create-organization/', OrganizationCreateView.as_view(), name='create-organization'),
    path('job-opening-update/<int:pk>/', JobOpeningUpdateView.as_view(), name='job-opening-update'),
    path('job-opening-delete/<int:pk>/', JobOpeningDeleteView.as_view(), name='job-opening-delete'),
    path('application-create/<int:pk>/', ApplicationCreateView.as_view(), name='application_create'),
    path('application-success/<int:pk>/', ApplicationSuccessView.as_view(), name='application_success'),
]
