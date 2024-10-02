"""
URL configuration for recruit_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from users.forms import EmailValidationOnForgotPassword
from users.views import (UserDetailView, SettingsView, CustomLoginView,
                         ClientsListView,EmployeeListView, CompanyCreateView, EmployeeDeleteView,
                         ClientDeleteView, EmployeeUpdateView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('screening/', include('screening.urls')),
    path('', include('dashboard.urls')),
    path('manager/', include('manager.urls')),
    path('notification/', include('notification.urls')),
    path('candidate/', include('candidate.urls')),
    path('adminuser/', include('adminuser.urls')),
    path('register/', user_views.register, name='register'),
    path('users-details/<int:pk>/', UserDetailView.as_view(), name='users-details'),
    path('users-update/<int:pk>/', EmployeeUpdateView.as_view(), name='users-update'),
    path('company-create/', CompanyCreateView.as_view(), name='company-create'),
    path('users-settings/', SettingsView.as_view(), name='users-settings'),
    path('users-clients/', ClientsListView.as_view(), name='users-clients'),
    path('users-clients-delete/<int:pk>/', ClientDeleteView.as_view(), name='clients-delete'),
    path('users-employees/',EmployeeListView.as_view(),name='users-employees'),
    path('users-employees-delete/<int:pk>/',EmployeeDeleteView.as_view(),name='employees-delete'),
    path('password_reset/',
         lambda request: redirect('parsing-home') if request.user.is_authenticated else auth_views.PasswordResetView.as_view(form_class=EmailValidationOnForgotPassword, template_name='users/forgot-password-10.html')(request),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('verification/', include('verify_email.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
