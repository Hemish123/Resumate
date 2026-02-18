from .views import (JobOpeningCreateView, ClientCreateView, ClientUpdateView,
                    JobOpeningUpdateView, JobOpeningDeleteView)
from django.urls import path
from django.views.generic import TemplateView
from manager import views

urlpatterns = [
    path('job-opening-create/', JobOpeningCreateView.as_view(), name='job-opening-create'),
    path('create-client/', ClientCreateView.as_view(), name='create-client'),
    path('client-update/<int:pk>/', ClientUpdateView.as_view(), name='client-update'),

    path('job-opening-update/<int:pk>/', JobOpeningUpdateView.as_view(), name='job-opening-update'),
    path('job-opening-delete/<int:pk>/', JobOpeningDeleteView.as_view(), name='job-opening-delete'),
    path('job-opening-import/', views.job_opening_import, name='job-opening-import'),

    path('onboard-client/', views.client_onboarding, name='client_onboarding'),
    path('clients/', views.client_list, name='client_list'),  
    path('client/<int:pk>/', views.client_detail, name='client_detail'),
    path('export-clients/', views.export_clients, name='export_clients'),
    path("client/<int:pk>/delete/", views.client_delete, name="client_delete"),
    path("client/<int:pk>/update/", views.update_client, name="update_client"),







]
