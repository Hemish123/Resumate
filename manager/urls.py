from .views import JobOpeningCreateView
from django.urls import path


urlpatterns = [
    path('job-opening-create/', JobOpeningCreateView.as_view(), name='job-opening'),
]
