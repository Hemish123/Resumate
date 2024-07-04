from django.shortcuts import render
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import JobOpening, Organization
from .forms import JobOpeningForm
from django.views.generic.edit import FormView

import json

# Create your views here.
class JobOpeningCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = JobOpening
    fields = ['organization', 'designation', 'openings', 'requiredskills', 'jobdescription', 'assignemployee']
    template_name = "dashboard/job_opening_create.html"
    title = "Job-Opening"
    permission_required = 'manager.add_jobopening'  # Replace with actual permission codename
    success_url = ''

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_jobopening').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        form = JobOpeningForm()
        with open("dashboard/static/dashboard/json/designations.json") as f:
            data = json.load(f)

        context['form'] = form
        context['data'] = data
        return context