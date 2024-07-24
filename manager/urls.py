from .views import JobOpeningCreateView, OrganizationCreateView, JobOpeningUpdateView, JobOpeningDeleteView
from django.urls import path


urlpatterns = [
    path('job-opening-create/', JobOpeningCreateView.as_view(), name='job-opening'),
    path('create-organization/', OrganizationCreateView.as_view(), name='create-organization'),
    path('job-opening-update/<int:pk>/', JobOpeningUpdateView.as_view(), name='job-opening-update'),
    path('job-opening-delete/<int:pk>/', JobOpeningDeleteView.as_view(), name='job-opening-delete'),
]
