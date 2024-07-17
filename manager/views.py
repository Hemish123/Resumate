import requests
from django.shortcuts import render
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import JobOpening, Organization
from users.models import Employee
from .forms import JobOpeningForm
from django.views.generic.edit import FormView

import json

# Create your views here.
class JobOpeningCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = JobOpening
    fields = ['organization', 'designation', 'openings', 'budget', 'job_type', 'job_mode',
              'requiredskills', 'jobdescription', 'assignemployee']
    template_name = "manager/job_opening_create.html"
    title = "Job-Opening"
    permission_required = 'manager.add_jobopening'  # Replace with actual permission codename
    # success_url = reverse_lazy('dashboard')

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_jobopening').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['choices'] = Employee.objects.all()
        context['organizations'] = Organization.objects.all()
        with open("dashboard/static/dashboard/json/designations.json") as f:
            data = json.load(f)

        with open("dashboard/static/dashboard/json/skills.json") as f:
            skills = json.load(f)


        context['skills'] = skills
        context['data'] = data
        return context

    def form_valid(self, form):
        if self.request.POST:
            job_opening = form.save(commit=False)
            organization = form.cleaned_data['organization']
            designation = form.cleaned_data['designation']
            required_skills = self.request.POST.getlist('requiredskills')

            # Convert list of skills to a string (comma-separated or JSON format)
            selected_skills = ",".join(required_skills)
            job_opening.requiredskills = selected_skills
            if JobOpening.objects.filter(organization=organization, designation=designation).exists():
                form.add_error('organization', 'opening already exists')
                return self.form_invalid(form)
            messages.success(self.request, message='Opening created successfully!')
            return super().form_valid(form)


class OrganizationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Organization
    fields = ['name', 'location', 'email', 'contact', 'website']
    template_name = "manager/create_organization.html"
    title = "Add New Organization"
    permission_required = 'manager.add_organization'  # Replace with actual permission codename
    # success_url = 'dashboard/dashboard.html'

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_organization').exists()


    def form_valid(self, form):
        messages.success(self.request, message='Organization created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = self.title
    #     form = JobOpeningForm()
    #     context['choices'] = Employee.objects.all()
    #     with open("dashboard/static/dashboard/json/designations.json") as f:
    #         data = json.load(f)
    #
    #     context['form'] = form
    #     context['data'] = data
    #     return context