from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.signals import post_save
from rest_framework.views import APIView
from django.db.models import Q

from dashboard.models import CandidateStage, Stage
from .models import Candidate, ResumeAnalysis
from users.models import Employee
from manager.models import JobOpening
# from .forms import CandidateForm
from django.utils import timezone
from datetime import datetime
from .resume_parsing.extract_text import extractText
from .resume_parsing.final_parsing import parse_data
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os, json, re
from django.conf import settings
from .genai_resume import get_response
from .forms import CandidateForm
from notification.models import Notification
from dashboard.utils import send_success_email, new_application_email


# Create your views here.
class CandidateCreateView(FormView):
    # model = Candidate
    form_class = CandidateForm

    template_name = "candidate/application_create.html"
    title = "Application"

    def get_success_url(self):
        return reverse_lazy('application_success', kwargs={'pk1': self.kwargs['pk'], 'pk2': self.candidate.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk'])
        context['job_opening'] = job_opening
        context['client'] = job_opening.client
        context['company'] = job_opening.company
        context['required_skills'] = job_opening.requiredskills.split(',')
        context['job_type'] = job_opening.job_type
        context['job_mode'] = job_opening.job_mode
        context['min_experience'] = job_opening.min_experience
        context['max_experience'] = job_opening.max_experience
        context['education'] = job_opening.education

        # Check the content type and assign the appropriate context variable

        if job_opening.content_type == 'file' and job_opening.jobdescription:

            context['job_description_file'] = job_opening.jobdescription

        elif job_opening.content_type == 'text' and job_opening.jd_content:

            context['job_description_text'] = job_opening.jd_content

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
        # context['clients'] = Client.objects.all()

        return context

    def post(self, request, *args, **kwargs):

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if the request is an AJAX request
            return self.handle_ajax(request)
        else:
            return self.handle_form_submission(request)

    def handle_ajax(self, request):
        form = self.get_form()
        if request.FILES.get('upload_resume'):

            resume_file = request.FILES['upload_resume']

            file_content = resume_file.read()

            # Use in-memory file handling with ContentFile if needed
            temp_file = ContentFile(file_content, resume_file.name)

            path = default_storage.save('resume/' + resume_file.name, temp_file)
            full_file_path = os.path.join(settings.MEDIA_ROOT, path)
            # file_path = resume_file.path
            extractedText = extractText(full_file_path)
            default_storage.delete(path)
            if extractedText.strip() == "" :
                form.add_error('upload_resume', (resume_file.name + ' cannot be parsed'))
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                parsed_data = parse_data(extractedText)

                request.session['resume'] = extractedText
                return JsonResponse({'success': True, 'parsed_data': parsed_data})


    def handle_form_submission(self, request):
        job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk'])
        # Create a form instance with the POST data
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            # candidate, created = Candidate.objects.get_or_create(email=email)
            if Candidate.objects.filter(email=email, company=job_opening.company).exists():
                candidate = Candidate.objects.get(email=email, company=job_opening.company)
                candidate.name = form.cleaned_data['name']
                candidate.contact = form.cleaned_data['contact']
                candidate.location = form.cleaned_data['location']
                candidate.education = form.cleaned_data['education']
                candidate.current_designation = form.cleaned_data['current_designation']
                candidate.experience = form.cleaned_data['experience']
                candidate.linkedin = form.cleaned_data['linkedin']
                candidate.github = form.cleaned_data['github']
                candidate.portfolio = form.cleaned_data['portfolio']
                candidate.blog = form.cleaned_data['blog']
                candidate.current_organization = form.cleaned_data['current_organization']
                candidate.updated = timezone.now()
                candidate.is_new = True
                # candidate.job_openings.add(job_opening)
            else:
                candidate = form.save(commit=False)
            resume = request.session.get('resume', None)

            if not resume:
                form.add_error(None, 'Resume data is missing. Please upload the resume again.')
                # return render(request, self.template_name, self.get_context_data())

                return self.form_invalid(form)

            # if Candidate.objects.filter(email=email, job_openings=job_opening, company=job_opening.company).exists():
            #     form.add_error(None, 'You have already applied for this role!')
            #     # return render(request, self.template_name, self.get_context_data())
            #     return self.form_invalid(form)

            del request.session['resume']
            file = request.FILES.get('upload_resume')

            # self.object = candidate
            # if created or candidate.upload_resume:
            candidate.upload_resume = file
            candidate.filename = file.name
            candidate.text_content = resume
            candidate.company = job_opening.company
            candidate.job_opening_id_temp = job_opening.id

            candidate.save()

            send_success_email(candidate, job_opening)

            candidate.job_openings.add(job_opening)

            message = candidate.name + " applied for " + job_opening.designation
            employees = job_opening.assignemployee.all()
            for e in employees:
                Notification.objects.create(user_id=e.user.id, message=message)
                site_url = self.request.META.get('HTTP_HOST')  # Get current domain for activation link
                new_application_email(candidate, job_opening, e, site_url)

            manager = job_opening.created_by
            if manager:
                Notification.objects.create(user_id=manager.id, message=message)

            self.candidate = candidate
            stage = Stage.objects.get(name='Applied', job_opening=job_opening)
            CandidateStage.objects.get_or_create(candidate=candidate, stage=stage)
            response_text = get_response(candidate.text_content, job_opening.designation,
                                         job_opening.requiredskills, str(job_opening.min_experience),
                                         str(job_opening.max_experience), job_opening.education)
            resume_analysis, _ = ResumeAnalysis.objects.get_or_create(candidate=candidate, job_opening=job_opening)
            resume_analysis.response_text = response_text
            resume_analysis.save()
            messages.success(self.request, message=f"Application created successfully for {job_opening.designation}!")
            # Process the final submission after user reviews the parsed data
            return self.form_valid(form)
            # return self.get_success_url()


        else:
            return self.form_invalid(form)

    # def form_invalid(self, form):
    #     self.object = None
    #     return super().form_invalid(form)

class ApplicationSuccessView(TemplateView):
    template_name = 'candidate/application_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk1'])
        candidate = get_object_or_404(Candidate, pk=self.kwargs['pk2'])
        candidate.job_openings.add(job_opening)
        context['job_opening'] = job_opening

        return context


class CandidateUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Candidate
    # form_class = CandidateForm
    fields = ['name', 'email', 'contact', 'location', 'dob', 'linkedin', 'github',
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

        return context

    def form_valid(self, form):
        if self.request.POST:
            candidate = form.save(commit=False)
            email = form.cleaned_data['email'].lower()

            # if form.cleaned_data['dob']:
            #     dob = form.cleaned_data['dob'].strftime('%d-%m-%Y')
            #     candidate.dob = datetime.strptime(dob, '%d-%m-%Y').date()
            #     print('d ', candidate.dob, dob)

            candidate.updated = timezone.now()

            if email and Candidate.objects.exclude(id=candidate.id).filter(email=email).exists():
                form.add_error('email', 'Email exists for another candidate!')
                return self.form_invalid(form)

            # client = form.cleaned_data['client']
            # designation = form.cleaned_data['designation']
            # required_skills = self.request.POST.getlist('requiredskills')

            messages.success(self.request, message='Candidate updated successfully!')
            return super().form_valid(form)

class CandidateListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/candidate_list.html'
    title = 'Candidate Database'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['candidates'] = Candidate.objects.filter(company=self.request.user.employee.company)

        return context

class ResumeListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/resume_list.html'
    title = 'Resume Database'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['candidates'] = Candidate.objects.filter(company=self.request.user.employee.company)

        return context


class ResumeSearchView(LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        if query:
            candidates = Candidate.objects.filter(
                Q(text_content__icontains=query),
                company=self.request.user.employee.company
            )
        else:
            candidates = Candidate.objects.filter(company=self.request.user.employee.company)

        results = []
        for candidate in candidates:
            results.append({
                'filename': candidate.filename,
                'resume_url': candidate.upload_resume.url,
                'content': candidate.text_content[:100],  # Limit to 100 characters or customize
                'updated': candidate.updated.strftime('%Y-%m-%d'),  # Customize as needed
            })
        return JsonResponse({'results': results})

class ApplicationListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/application_list.html'
    title = 'All Applications'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        id = self.kwargs.get('pk')
        job_opening = JobOpening.objects.get(pk=id)
        candidates = Candidate.objects.filter(job_openings=job_opening, company=self.request.user.employee.company).order_by('-is_new')
        context['job_opening'] = job_opening
        # relevant_candidates = []
        # non_relevant_candidates = []
        # for c in candidates:
        #     response_text = json.loads(ResumeAnalysis.objects.get(candidate=c, job_opening=job_opening).response_text)
        #     if response_text['skills_matching']['match'] >= 50:
        #         relevant_candidates.append(c)
        #     else :
        #         non_relevant_candidates.append(c)

        context['candidates'] = candidates

        # Candidate.objects.filter(job_openings=job_opening, company=self.request.user.employee.company, is_new=True).update(is_new=False)
        return context

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')

        return redirect(reverse('screening', kwargs={'pk': id}))

class CandidateDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'candidate/candidate_details.html'
    title = 'Candidate Details'
    model = Candidate
    context_object_name = 'candidate'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        job_opening_id = self.request.GET.get('job_opening_id')
        if job_opening_id :
            context['job_opening'] = JobOpening.objects.get(pk=job_opening_id)

        return context

class CandidateDeleteView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        
        ids = request.POST.get('ids[]')  # Get list of IDs from POST data
        print(ids)  
        if ids:
            ids = [int(id) for id in ids.split(',')]
            Candidate.objects.filter(id__in=ids).delete()  # Delete candidates with these IDs
        return JsonResponse({'status': 'success'})

class CandidateAnalysisView(LoginRequiredMixin, TemplateView):
    title = 'Resume Analysis'
    template_name = 'candidate/candidate_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        # text = json.loads(self.request.GET.get('response'))
        id = self.kwargs.get('pk')
        job_opening_id = self.request.GET.get('job_opening_id')
        candidate = Candidate.objects.get(id=id)
        candidate.is_new = False
        candidate.save()
        job_opening = candidate.job_openings.get(id=job_opening_id)

        if job_opening :
            context['job_opening'] = job_opening
            context['role'] = job_opening.designation
        response_text = ResumeAnalysis.objects.get(candidate=candidate, job_opening=job_opening).response_text
        context['response_text'] = response_text
        context['candidate'] = candidate
        text = json.loads(response_text)
        context['text'] = text
        stable = False
        print(response_text)
        if text.get('average_tenure') and "year" in text.get('average_tenure'):
            match = re.search(r'\d+', text.get('average_tenure'))
            if match:
                if float(match.group())>=1 :
                    stable = True
                else:

                    if text.get('current_tenure') and "year" in text.get('current_tenure'):
                        current_tenure = re.search(r'\d+', text.get('current_tenure'))
                        if current_tenure:
                            if float(current_tenure.group()) >= 2:
                                stable = True



        context['stable'] = stable
        return context
