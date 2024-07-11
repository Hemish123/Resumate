from django.urls import path
from . import views
from .views import DashbaordView, StageView,StageAPIView


urlpatterns = [
    path('', DashbaordView.as_view(), name='dashboard'),
    path('job-process/<int:pk>', StageView.as_view(), name='job-process'),
    path('stage-api/<int:pk>', StageAPIView.as_view(), name='stage-api')
]

