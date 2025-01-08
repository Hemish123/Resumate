import requests
from django.shortcuts import render,get_object_or_404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin

from dashboard.utils import new_opening_email
from .models import JobOpening, Client
from users.models import Employee
from dashboard.models import Stage
from .forms import JobOpeningForm
from django.views.generic.edit import FormView
from candidate.resume_parsing.extract_text import extractText
from notification.models import Notification

import json

# Create your views here.
class JobOpeningCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = JobOpening
    fields = ['client', 'designation', 'openings', 'budget', 'job_type', 'job_mode',
              'requiredskills', 'jobdescription', 'assignemployee', 'jd_content', 'min_experience',
              'max_experience', 'education', 'content_type', 'skills_criteria']
    template_name = "manager/job_opening_create.html"
    title = "Job-Opening"
    permission_required = 'manager.add_jobopening'  # Replace with actual permission codename
    success_url = reverse_lazy('dashboard')

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_jobopening').exists()

    def get(self, request, *args, **kwargs):
        self.request.session['previous_page'] = request.path
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['choices'] = Employee.objects.filter(company=self.request.user.employee.company)
        context['clients'] = Client.objects.filter(company=self.request.user.employee.company)

        # Load JSON data for designations and skills
        # with open("dashboard/static/dashboard/json/designations.json") as f:
        #     context['data'] = json.load(f)

        with open("dashboard/static/dashboard/json/skills.json") as f:
            context['skills'] = json.load(f)

        return context

    def form_valid(self, form):
        if self.request.POST:
            job_opening = form.save(commit=False)
            job_opening.company = self.request.user.employee.company
            client = form.cleaned_data['client']
            designation = form.cleaned_data['designation']
            jd_content = form.cleaned_data['jd_content']
            file = form.cleaned_data['jobdescription']
            employees = form.cleaned_data['assignemployee']
            
            # Extract and process required skills
            required_skills = self.request.POST.get('requiredskills')
            if required_skills:
                skills_list = json.loads(required_skills)
                skills_string = ', '.join([skill['value'] for skill in skills_list])
                job_opening.requiredskills = skills_string
            
            # Check if the job opening already exists
            if client :
                if JobOpening.objects.filter(company=self.request.user.employee.company, client=client, designation=designation).exists():
                    form.add_error('client', 'Opening already exists')
                    return self.form_invalid(form)
            else:
                if JobOpening.objects.filter(company=self.request.user.employee.company ,designation=designation).exists():
                    form.add_error('designation', 'Opening already exists')
                    return self.form_invalid(form)
             
            # Save the job opening and create default stages
            job_opening.save()
            message = "New Job Opening " + job_opening.designation + " assigned to you"
            for e in employees:
                Notification.objects.create(user_id=e.user.id, message=message)
                new_opening_email(job_opening, e)

            if file and not jd_content:
                jd_content = extractText(job_opening.jobdescription.path)
                job_opening.jd_content = jd_content
            Stage.objects.create(job_opening_id=job_opening.id, name='Applied', order=1)
            Stage.objects.create(job_opening_id=job_opening.id, name='Initial Stage', order=2)
            Stage.objects.create(job_opening_id=job_opening.id, name='Rejected', order=40)
            Stage.objects.create(job_opening_id=job_opening.id, name='Hired', order=50)

            messages.success(self.request, 'Opening created successfully!')
            return super().form_valid(form)

        
class JobOpeningUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = JobOpening
    fields = ['client', 'designation', 'openings', 'budget', 'job_type', 'job_mode',
              'requiredskills', 'jobdescription', 'assignemployee', 'jd_content', 'min_experience',
              'max_experience', 'education', 'content_type', 'skills_criteria', 'active']
    template_name = "manager/job_opening_update.html"
    title = "Job-Opening-Update"
    permission_required = 'manager.change_jobopening'  # Replace with actual permission codename

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='change_jobopening').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['choices'] = Employee.objects.filter(company=self.request.user.employee.company)
        if self.object.hiring_for == "client":
            context['clients'] = Client.objects.filter(company=self.request.user.employee.company)
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
            client = job_opening.client
            jd_content = form.cleaned_data['jd_content']
            file = form.cleaned_data['jobdescription']
            designation = form.cleaned_data['designation']
            employees = form.cleaned_data['assignemployee']
            required_skills = self.request.POST.get('requiredskills')
            if required_skills:
                skills_list = json.loads(required_skills)
                skills_string = ', '.join([skill['value'] for skill in skills_list])
                job_opening.requiredskills = skills_string

            if client :
                if JobOpening.objects.exclude(id=job_opening.id).filter(company=self.request.user.employee.company, client=client, designation=designation).exists():
                    form.add_error('client', 'opening already exists')
                    return self.form_invalid(form)
            else:
                if JobOpening.objects.exclude(id=job_opening.id).filter(company=self.request.user.employee.company, designation=designation).exists():
                    form.add_error('designation', 'opening already exists')
                    return self.form_invalid(form)

            message = "New Job Opening " + job_opening.designation + " assigned to you"
            for e in employees:
                if not Notification.objects.filter(user_id=e.user.id, message=message).exists():
                    Notification.objects.create(user_id=e.user.id, message=message)
                    new_opening_email(job_opening, e)

            if file and not jd_content:
                jd_content = extractText(job_opening.jobdescription.path)
                job_opening.jd_content = jd_content

            messages.success(self.request, message='Opening updated successfully!')

            return super().form_valid(form)

class JobOpeningDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = JobOpening
    success_url = reverse_lazy('dashboard')
    permission_required = 'manager.delete_jobopening'

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='delete_jobopening').exists()

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    fields = ['name', 'location', 'email', 'contact', 'website']
    template_name = "manager/create_client.html"
    title = "Add New Client"
    permission_required = 'manager.add_client'  # Replace with actual permission codename
    # success_url = 'dashboard/dashboard.html'

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_client').exists()


    def form_valid(self, form):
        client = form.save(commit=False)
        client.company = self.request.user.employee.company
        client.save()
        messages.success(self.request, message='Client created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        previous_page = self.request.session.get('previous_page')
        print('r', previous_page)
        if previous_page and ('job-opening-create' in previous_page):
            self.request.session['previous_page'] = ''
            return reverse_lazy('job-opening')
        return reverse_lazy('dashboard')

class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    fields = ['name', 'location', 'email', 'contact', 'website']
    template_name = "manager/update_client.html"
    title = "Update Client"
    permission_required = 'manager.change_client'  # Replace with actual permission codename
    success_url = reverse_lazy('users-settings')

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='change_client').exists()


    def form_valid(self, form):

        messages.success(self.request, message='Client updated successfully!')
        return super().form_valid(form)
