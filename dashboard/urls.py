from django.urls import path
from . import views
from .views import DashbaordView, StageView


urlpatterns = [
    path('', DashbaordView.as_view(), name='dashboard'),
    path('job-process/', StageView.as_view(), name='job-process'),

]

