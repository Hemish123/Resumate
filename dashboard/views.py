from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin

from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json




class DashbaordView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    title = 'Dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['user'] = self.request.user
        # Access permission details (optional)
        has_perm = self.request.user.groups.filter(permissions__codename='add_jobopening').exists()
        context['has_perm'] = has_perm

        context['job_posts'] = [{"designation" : "Python Developer",
                                 "company": "JMS Advisory", "open": "Open Positions : 2", "alert": "primary", "status": "Active"},
                                {"designation": "Web Developer",
                                 "company": "XYZ Organization", "open": "Open Positions : 3", "alert": "danger", "status": "Closed"}
                                ]
        return context


class StageView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/stages.html'
    title = 'Job Process'



# class ContactUsView(FormView):
#     template_name = 'screening/contactus.html'
#     form_class = ContactForm
#     success_url = '/contactus/'  # Adjust this as needed
#
#     def form_valid(self, form):
#         name = form.cleaned_data['name']
#         email = form.cleaned_data['email']
#         message = form.cleaned_data['message']
#
#         # Send email
#         send_mail(
#             'New Contact Us Submission',
#             f'Name: {name}\nEmail: {email}\nMessage: {message}',
#             settings.DEFAULT_FROM_EMAIL,
#             ['resumate1nfo1@gmail.com'],
#             fail_silently=False,
#         )
#
#         return JsonResponse({'success': True})
#
#     def form_invalid(self, form):
#         return JsonResponse({'success': False, 'errors': form.errors}, status=400)
