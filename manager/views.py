import requests
from django.shortcuts import render,get_object_or_404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import JobOpening, Organization, Application
from users.models import Employee
from dashboard.models import Stage
from .forms import JobOpeningForm
from django.views.generic.edit import FormView

import json

# Create your views here.
class JobOpeningCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = JobOpening
    fields = ['organization', 'designation', 'openings', 'budget', 'job_type', 'job_mode',
              'requiredskills', 'jobdescription', 'assignemployee', 'jd_content', 'content_type']
    template_name = "manager/job_opening_create.html"
    title = "Job-Opening"
    permission_required = 'manager.add_jobopening'  # Replace with actual permission codename
    success_url = reverse_lazy('dashboard')

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_jobopening').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['choices'] = Employee.objects.all()
        context['organizations'] = Organization.objects.all()

        # Load JSON data for designations and skills
        with open("dashboard/static/dashboard/json/designations.json") as f:
            context['data'] = json.load(f)

        with open("dashboard/static/dashboard/json/skills.json") as f:
            context['skills'] = json.load(f)

        return context

    def form_valid(self, form):
        if self.request.POST:
            job_opening = form.save(commit=False)
            organization = form.cleaned_data['organization']
            designation = form.cleaned_data['designation']
            jd_content = form.cleaned_data['jd_content']
            
            # Extract and process required skills
            required_skills = self.request.POST.get('requiredskills')
            if required_skills:
                skills_list = json.loads(required_skills)
                skills_string = ', '.join([skill['value'] for skill in skills_list])
                job_opening.requiredskills = skills_string
            
            # Check if the job opening already exists
            if JobOpening.objects.filter(organization=organization, designation=designation).exists():
             form.add_error('organization', 'Opening already exists')
             self.form_invalid(form)
             
            # Save the job opening and create default stages
            job_opening.save()
            Stage.objects.create(job_opening_id=job_opening.id, name='Initial Stage', order=1)
            Stage.objects.create(job_opening_id=job_opening.id, name='Hired', order=50)

            messages.success(self.request, 'Opening created successfully!')
            return super().form_valid(form)
        
class JobOpeningUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = JobOpening
    fields = ['organization', 'designation', 'openings', 'budget', 'job_type', 'job_mode',
              'requiredskills', 'jobdescription', 'assignemployee', 'active']
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
            if JobOpening.objects.exclude(id=job_opening.id).filter(organization=organization, designation=designation).exists():
                form.add_error('organization', 'opening already exists')
                return self.form_invalid(form)
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

class ApplicationCreateView(TemplateView):
    template_name = 'manager/application_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk'])
        context['job_opening'] = job_opening
        context['organization'] = job_opening.organization
        context['required_skills'] = job_opening.requiredskills.split(',')
        context['job_type'] = job_opening.job_type
        context['job_mode'] = job_opening.job_mode

 
        # Check the content type and assign the appropriate context variable
    
        if job_opening.content_type == 'file' and job_opening.jobdescription:

            context['job_description_file'] = job_opening.jobdescription
            
        elif job_opening.content_type == 'text' and job_opening.jd_content:

            context['job_description_text'] = job_opening.jd_content
            

        return context

    def post(self, request, *args, **kwargs):
        job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk'])
        file_upload = request.FILES.get('file_upload')

        if not file_upload:
            messages.error(request, "Please upload a file.")
            return self.render_to_response(self.get_context_data(**kwargs))

        application = Application.objects.create(
            job_opening=job_opening,
            file_upload=file_upload
        )
        application.save()
        
        messages.success(request, f"Application created successfully for {job_opening.designation}!")
        return HttpResponseRedirect(reverse('application_success', kwargs={'pk': job_opening.pk}))

# class ApplicationSuccessView(TemplateView):
#     template_name = 'manager/application_success.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk'])
#         context['job_opening'] = job_opening
#         return contextclass ApplicationCreateView(TemplateView):
    
class ApplicationSuccessView(TemplateView):
    template_name = 'manager/application_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk'])
        context['job_opening'] = job_opening
        return context