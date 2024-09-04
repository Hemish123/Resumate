from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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

# Create your views here.
class CandidateCreateView(CreateView):
    model = Candidate
    # form_class = CandidateForm
    fields = ['job_openings', 'name', 'email', 'contact', 'location', 'dob', 'linkedin', 'github',
              'portfolio', 'blog', 'education', 'experience', 'current_designation', 'current_organization',
              'current_ctc', 'current_ctc_ih', 'expected_ctc', 'expected_ctc_ih',
              'offer_in_hand', 'notice_period', 'reason_for_change', 'feedback', 'upload_resume']
    template_name = "candidate/application_create.html"
    title = "Application"

    def get_success_url(self):
        candidate_id = self.request.session.get('candidate_id')
        return reverse_lazy('application_success', kwargs={'pk1': self.kwargs['pk'], 'pk2': candidate_id})

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

    # def form_valid(self, form):
    #     if self.request.POST:
    #         # if form.cleaned_data['dob']:
    #         #     dob = form.cleaned_data['dob'].strftime('%d-%m-%Y')
    #         #     candidate.dob = datetime.strptime(dob, '%d-%m-%Y').date()
    #         #     print('d ', candidate.dob, dob)
    #         # if form.cleaned_data['doc']:
    #         #     doc = form.cleaned_data['doc'].strftime('%d-%m-%Y')
    #         #     candidate.doc = datetime.strptime(doc, '%d-%m-%Y').date()
    #         #     print('c ', candidate.doc, doc)
    #         # else:
    #         #     candidate.doc = timezone.now().date()
    #
    #         # client = form.cleaned_data['client']
    #         # designation = form.cleaned_data['designation']
    #         # required_skills = self.request.POST.getlist('requiredskills')
    #
    #         # user = self.request.user
    #         # candidate.created_by = user
    #
    #         # if JobOpening.objects.filter(client=client, designation=designation).exists():
    #         #     form.add_error('client', 'opening already exists')
    #         #     return self.form_invalid(form)
    #         return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

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
            candidate = form.save(commit=False)
            email = form.cleaned_data['email'].lower()
            resume = request.session.get('resume', None)
            if not resume:
                form.add_error(None, 'Resume data is missing. Please upload the resume again.')
                return self.form_invalid(form)
            file = request.FILES.get('upload_resume')
            candidate.upload_resume = file
            candidate.filename = file.name
            candidate.text_content = resume
            if Candidate.objects.filter(email=email, job_openings=job_opening).exists():
                form.add_error('email', 'You have already applied!')
                return self.form_invalid(form)
            self.object = candidate
            candidate.save()  # Save the candidate
            candidate.job_openings.set([job_opening])
            self.request.session['candidate_id'] = candidate.id

            # Clean up session
            del request.session['resume']
            response_text = get_response(candidate.text_content, job_opening.designation,
                                         job_opening.requiredskills, str(job_opening.min_experience),
                                         str(job_opening.max_experience), job_opening.education)
            ResumeAnalysis.objects.create(response_text=response_text, candidate=candidate)
            messages.success(self.request, message=f"Application created successfully for {job_opening.designation}!")
            # Process the final submission after user reviews the parsed data
            return self.form_valid(form)

        else:
            return self.form_invalid(form)


class ApplicationSuccessView(TemplateView):
    template_name = 'candidate/application_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk1'])
        candidate = get_object_or_404(Candidate, pk=self.kwargs['pk2'])
        context['job_opening'] = job_opening
        context['role'] = job_opening.designation
        response_text = ResumeAnalysis.objects.get(candidate=candidate).response_text
        context['response_text'] = response_text
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
        # context['clients'] = Client.objects.all()

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

            # client = form.cleaned_data['client']
            # designation = form.cleaned_data['designation']
            # required_skills = self.request.POST.getlist('requiredskills')

            user = self.request.user
            candidate.created_by = user

            # if JobOpening.objects.filter(client=client, designation=designation).exists():
            #     form.add_error('client', 'opening already exists')
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
