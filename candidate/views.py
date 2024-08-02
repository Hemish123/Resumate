from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .models import Candidate, Resume
from users.models import Employee
from manager.models import JobOpening
# from .forms import CandidateForm
from django.utils import timezone
from datetime import datetime
from django.views.generic.edit import FormView

import json

# Create your views here.
class CandidateCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Candidate
    # form_class = CandidateForm
    fields = ['job_openings', 'name', 'email', 'contact', 'location', 'dob', 'doc', 'linkedin', 'github',
              'portfolio', 'blog', 'education', 'experience', 'current_designation', 'current_organization',
              'current_ctc', 'current_ctc_ih', 'expected_ctc', 'expected_ctc_ih',
              'offer_in_hand', 'notice_period', 'reason_for_change', 'feedback']
    template_name = "candidate/candidate_create.html"
    title = "Create Candidate"
    permission_required = 'candidate.add_candidate'  # Replace with actual permission codename
    success_url = reverse_lazy('dashboard')

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_candidate').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        try:
            if self.request.user.is_superuser or self.request.user.groups.filter(
                    name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
                context['choices'] = JobOpening.objects.all()
            else :
                employee = Employee.objects.get(user=self.request.user)
                context['choices'] = JobOpening.objects.filter(assignemployee=employee)
        except Employee.DoesNotExist:
            context['choices'] = JobOpening.objects.all()
        # context['organizations'] = Organization.objects.all()

        return context

    def form_valid(self, form):
        if self.request.POST:
            candidate = form.save(commit=False)
            email = form.cleaned_data['email'].lower()

            # if form.cleaned_data['dob']:
            #     dob = form.cleaned_data['dob'].strftime('%d-%m-%Y')
            #     candidate.dob = datetime.strptime(dob, '%d-%m-%Y').date()
            #     print('d ', candidate.dob, dob)
            if form.cleaned_data['doc']:
                doc = form.cleaned_data['doc'].strftime('%d-%m-%Y')
                candidate.doc = datetime.strptime(doc, '%d-%m-%Y').date()
                print('c ', candidate.doc, doc)
            else:
                candidate.doc = timezone.now().date()

            if Candidate.objects.filter(email=email).exists():
                form.add_error('email', 'Email already exists!')
                return self.form_invalid(form)

            # organization = form.cleaned_data['organization']
            # designation = form.cleaned_data['designation']
            # required_skills = self.request.POST.getlist('requiredskills')

            user = self.request.user
            candidate.created_by = user

            # if JobOpening.objects.filter(organization=organization, designation=designation).exists():
            #     form.add_error('organization', 'opening already exists')
            #     return self.form_invalid(form)
            messages.success(self.request, message='Candidate created successfully!')
            return super().form_valid(form)

class CandidateUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Candidate
    # form_class = CandidateForm
    fields = ['job_openings', 'name', 'email', 'contact', 'location', 'dob', 'doc', 'linkedin', 'github',
              'portfolio', 'blog', 'education', 'experience', 'current_designation', 'current_organization',
              'current_ctc', 'current_ctc_ih', 'expected_ctc', 'expected_ctc_ih',
              'offer_in_hand', 'notice_period', 'reason_for_change', 'feedback']
    template_name = "candidate/candidate_update.html"
    title = "Update Candidate"
    permission_required = 'candidate.change_candidate'  # Replace with actual permission codename

    def get_success_url(self):
        return reverse_lazy('candidate-details', kwargs={'pk': self.object.pk})

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='change_candidate').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        try:
            if self.request.user.is_superuser or self.request.user.groups.filter(
                    name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
                context['choices'] = JobOpening.objects.all()
            else:
                employee = Employee.objects.get(user=self.request.user)
                context['choices'] = JobOpening.objects.filter(assignemployee=employee)
        except Employee.DoesNotExist:
            context['choices'] = JobOpening.objects.all()
        # context['organizations'] = Organization.objects.all()

        return context

    def form_valid(self, form):
        if self.request.POST:
            candidate = form.save(commit=False)
            email = form.cleaned_data['email'].lower()

            # if form.cleaned_data['dob']:
            #     dob = form.cleaned_data['dob'].strftime('%d-%m-%Y')
            #     candidate.dob = datetime.strptime(dob, '%d-%m-%Y').date()
            #     print('d ', candidate.dob, dob)
            if form.cleaned_data['doc']:
                doc = form.cleaned_data['doc'].strftime('%d-%m-%Y')
                candidate.doc = datetime.strptime(doc, '%d-%m-%Y').date()


            candidate.updated = timezone.now()

            if email and Candidate.objects.exclude(id=candidate.id).filter(email=email).exists():
                form.add_error('email', 'Email already exists!')
                return self.form_invalid(form)

            # organization = form.cleaned_data['organization']
            # designation = form.cleaned_data['designation']
            # required_skills = self.request.POST.getlist('requiredskills')

            user = self.request.user
            candidate.created_by = user

            # if JobOpening.objects.filter(organization=organization, designation=designation).exists():
            #     form.add_error('organization', 'opening already exists')
            #     return self.form_invalid(form)
            messages.success(self.request, message='Candidate updated successfully!')
            return super().form_valid(form)

class CandidateListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/candidate_list.html'
    title = 'Candidate Database'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['candidates'] = Candidate.objects.all()

        return context


class CandidateDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'candidate/candidate_details.html'
    title = 'Candidate Details'
    model = Candidate
    context_object_name = 'candidate'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title

        return context

class CandidateDeleteView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        
        ids = request.POST.get('ids[]')  # Get list of IDs from POST data
        print(ids)  
        if ids:
            ids = [int(id) for id in ids.split(',')]
            Candidate.objects.filter(id__in=ids).delete()  # Delete candidates with these IDs
        return JsonResponse({'status': 'success'})
