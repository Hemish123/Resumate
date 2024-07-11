from .views import JobOpeningCreateView, OrganizationCreateView
from django.urls import path


urlpatterns = [
    path('job-opening-create/', JobOpeningCreateView.as_view(), name='job-opening'),
    path('create-organization/', OrganizationCreateView.as_view(), name='create-organization'),
]
