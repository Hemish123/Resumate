from django.urls import path
from . import views
from .views import (ResumeListView, ResumeCreateView,
                    ScreeningView, ScreeningListView, ResumeDeleteView, AnalyticsTemplateView, ResumeView, ContactUsView)


urlpatterns = [
    path('', ResumeListView.as_view(), name='parsing-home'),
    path('screening/', ScreeningView.as_view(), name='screening'),
    path('upload/', ResumeCreateView.as_view(), name='parsing-upload'),
    path('resume/delete/<int:pk>', ResumeDeleteView.as_view(), name='parsing-delete'),
    path('screening/', ScreeningListView.as_view(), name='parsing-screening'),
    path('analytics/', AnalyticsTemplateView.as_view(), name='parsing-analytics'),
    path('about/', views.about, name='parsing-about'),
    path('resumes/', ResumeView.as_view(), name='parsing-resumes'),
    path('contactus/', ContactUsView.as_view(),name='parsing-contactus')
]

