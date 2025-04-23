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
from .forms import CandidateForm, CandidateImportForm
from notification.models import Notification
from dashboard.utils import send_success_email, new_application_email, send_job_opening_email
import csv, openpyxl
from django.db.models import Prefetch


class CandidateImportView(LoginRequiredMixin, FormView):
    template_name = "candidate/candidate_import.html"
    title = "Import Candidates"
    form_class = CandidateImportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            file = form.cleaned_data['upload_file']
            skip = 0
            if file.name.endswith('.xlsx'):
                workbook = openpyxl.load_workbook(file)
                sheet = workbook.active

                for row in sheet.iter_rows(min_row=2, values_only=True):  # Skipping header
                    name, contact, email1, *rest = row  # Unpack first three columns into name, email, contact
                    if name and ('@' in str(email1).strip()) and (len(str(contact))>=10):   # Check if row is not empty
                        email = row[2].lower() if isinstance(row[2], str) else None
                        if email:
                            if not Candidate.objects.filter(email=email, company=request.user.employee.company).exists():
                                try:
                                    experience = int(row[5])
                                except (ValueError, TypeError):
                                    experience = 0
                                #
                                # if not row[3]:
                                #     row[3] = None
                                # if not row[4]:
                                #     row[4] = None
                                Candidate.objects.create(
                                    name=row[0],
                                    contact=row[1],
                                    email=row[2],
                                    current_designation=row[3],
                                    location=row[4],
                                    experience=experience,
                                    company=request.user.employee.company
                                )
                            else:
                                skip += 1
                        else:
                            skip += 1
                    else:
                        skip += 1

            elif file.name.endswith('.csv'):
                try:
                    # Attempt decoding with a fallback encoding
                    decoded_file = file.read().decode('utf-8', errors='ignore').splitlines()
                except UnicodeDecodeError:
                    # Fallback to a lenient encoding
                    decoded_file = file.read().decode('latin1').splitlines()
                reader = csv.reader(decoded_file)
                # Skipping the header row (optional)
                next(reader, None)
                for row in reader:
                    email = row[2].lower() if isinstance(row[2], str) else None
                    if email:
                        if not Candidate.objects.filter(email=email,
                                                        company=request.user.employee.company).exists():
                            try:
                                experience = int(row[5])
                            except (ValueError, TypeError):
                                experience = 0

                            Candidate.objects.create(
                                name=row[0],
                                contact=row[1],
                                email=row[2],
                                current_designation=row[3],
                                location=row[4],
                                experience=experience,
                                company=request.user.employee.company
                            )
                            print('candidate')
                        else:
                            skip += 1
                    else:
                        skip += 1

            else:
                messages.error(request, "Invalid file format! Please upload CSV or Excel file.")
                return redirect('candidate-list')
            messages.success(request, f"Candidates imported successfully. skipped: {skip}")
            return redirect('candidate-list')

        else:
            return self.form_invalid(form)

# Create your views here.
class CandidateCreateView(FormView):
    # model = Candidate
    form_class = CandidateForm

    template_name = "candidate/application_create.html"
    title = "Application"

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse_lazy('candidate-analysis', kwargs={'pk': self.candidate.pk}) + f"?job_opening_id={self.kwargs['pk']}"
        else:
            return reverse_lazy('application_success', kwargs={'pk1': self.kwargs['pk'], 'pk2': self.candidate.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_opening = get_object_or_404(JobOpening, pk=self.kwargs['pk'])
        job_opening.request = self.request
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
        # try:
        #     if self.request.user.is_superuser or self.request.user.groups.filter(
        #             name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
        #         context['choices'] = JobOpening.objects.all()
        #     else :
        #         employee = Employee.objects.get(user=self.request.user)
        #         context['choices'] = JobOpening.objects.filter(assignemployee=employee)
        # except Employee.DoesNotExist:
        #     context['choices'] = JobOpening.objects.all()
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
            # Download from Azure and write to a local file
            # Define a temporary local path
            local_temp_path = f"/tmp/{resume_file.name}"

            # Download from Azure and write to a local file
            with open(local_temp_path, "wb") as f:
                f.write(default_storage.open(path).read())
            # full_file_path = os.path.join(settings.MEDIA_ROOT, path)
            # file_path = resume_file.path
            extractedText = extractText(local_temp_path)
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
            response_text = get_response(candidate.text_content, job_opening.designation,
                                         job_opening.requiredskills, str(job_opening.min_experience),
                                         str(job_opening.max_experience), job_opening.education)
            resume_analysis, _ = ResumeAnalysis.objects.get_or_create(candidate=candidate, job_opening=job_opening)
            resume_analysis.response_text = response_text
            resume_analysis.save()

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
            stages = Stage.objects.filter(job_opening=job_opening)
            if not CandidateStage.objects.filter(candidate=candidate, stage__in=stages).exists():
                stage = Stage.objects.get(name='Applied', job_opening=job_opening)
                CandidateStage.objects.get_or_create(candidate=candidate, stage=stage)



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

from django.core.paginator import Paginator
from django.http import JsonResponse

def candidate_list_api(request):
    search_value = request.GET.get('search[value]', '').strip()
    experience_filter = request.GET.get('experience', '').strip()
    status_filter = request.GET.get('status', '').strip()
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    draw = int(request.GET.get('draw', 1))

    # Sorting
    order_column_index = request.GET.get('order[0][column]', '9')
    order_dir = request.GET.get('order[0][dir]', 'desc')
    column_mapping = {
        "1": "id",
        "2": "name",
        "3": "current_designation",
        "4": "contact",
        "5": "email",
        "6": "location",
        "7": "experience",
        "9": "updated",
    }
    sort_field = column_mapping.get(order_column_index, 'updated')
    if order_dir == 'desc':
        sort_field = f"-{sort_field}"

    # Prefetch related CandidateStage objects
    candidatestage_queryset = Prefetch(
        'candidatestage_set',
        queryset=CandidateStage.objects.select_related('stage').only('stage__name')
    )

    # Base QuerySet
    base_queryset = Candidate.objects.filter(company=request.user.employee.company).prefetch_related(candidatestage_queryset).only(
        'id', 'name', 'current_designation', 'email', 'contact',
        'location', 'experience', 'updated', 'company_id'
    ).order_by(sort_field)

    total_records = base_queryset.count()

    # Apply filters
    filters = Q()

    if search_value:
        keywords = [word.strip() for word in search_value.replace(',', ' ').split()]
        for keyword in keywords:
            filters &= (
                Q(name__icontains=keyword) |
                Q(email__icontains=keyword) |
                Q(contact__icontains=keyword) |
                Q(location__icontains=keyword) |
                Q(current_designation__icontains=keyword)
            )

    if experience_filter:
        try:
            if experience_filter.isdigit():
                filters &= Q(experience=int(experience_filter))
            else:
                comparator, exp_value = experience_filter.split()
                exp_value = float(exp_value)
                if comparator == '<':
                    filters &= Q(experience__lt=exp_value)
                elif comparator == '>':
                    filters &= Q(experience__gt=exp_value)
                elif comparator == '=':
                    filters &= Q(experience=exp_value)
        except ValueError:
            pass

    if status_filter:
        status_list = [s.strip() for s in status_filter.split(',') if s.strip()]
        filters &= Q(candidatestage__stage__name__in=status_list)

    filtered_queryset = base_queryset.filter(filters).distinct()
    records_filtered = filtered_queryset.count()

    # Slice QuerySet (pagination)
    candidates = filtered_queryset[start:start + length]

    # Build data
    data = []
    for c in candidates:
        # Create the 'status' string by joining all related stages
        status = ', '.join([stage.stage.name for stage in c.candidatestage_set.all()])
        data.append({
            'id': c.id,
            'name': c.name,
            'designation': c.current_designation,
            'email': c.email,
            'contact': c.contact,
            'location': c.location,
            'experience': c.experience,
            'status': status or '',
            'updated': c.updated.strftime('%d-%m-%Y %H:%M')
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': records_filtered,
        'data': data
    })


    # # Get search term and filters from request
    # search_value = request.GET.get('search[value]', '').strip()
    # experience_filter = request.GET.get('experience', '').strip()
    # # candidates = Candidate.objects.filter(company=request.user.employee.company).order_by('-updated')
    #
    # # Get column index and sorting direction from request
    # order_column_index = request.GET.get('order[0][column]', None)
    # order_dir = request.GET.get('order[0][dir]', 'asc')
    #
    # # Define mapping of DataTables column index to model field names
    # column_mapping = {
    #     "0": "",
    #     "1": "id",
    #     "2": "name",
    #     "3": "current_designation",
    #     "4": "contact",
    #     "5": "email",
    #     "6": "location",
    #     "7": "experience",
    #     "9": "updated",
    # }
    #
    # # Apply sorting if valid column index is provided
    # if order_column_index in column_mapping:
    #     order_field = column_mapping[order_column_index]
    #     if order_dir == 'desc':
    #         order_field = f"-{order_field}"  # Add "-" for descending order
    #     candidates = candidates.order_by(order_field)
    #
    #
    # # Apply search filter
    # if search_value:
    #     keywords = [word.strip() for word in search_value.replace(',', ' ').split() if word.strip()]
    #     query_filter = Q()
    #     for keyword in keywords:
    #         query_filter &= (Q(name__icontains=keyword) |
    #         Q(email__icontains=keyword) |
    #         Q(contact__icontains=keyword) |
    #         Q(location__icontains=keyword) |
    #         Q(current_designation__icontains=keyword))
    #     candidates = candidates.filter(
    #         query_filter
    #     )
    #
    # # Apply experience filter
    # if experience_filter:
    #     try:
    #         if experience_filter.isdigit():
    #             candidates = candidates.filter(experience=int(experience_filter))
    #         else:
    #             comparator, exp_value = experience_filter.split()
    #             exp_value = float(exp_value)
    #             if comparator == '<':
    #                 candidates = candidates.filter(experience__lt=exp_value)
    #             elif comparator == '>':
    #                 candidates = candidates.filter(experience__gt=exp_value)
    #             elif comparator == '=':
    #                 candidates = candidates.filter(experience=exp_value)
    #     except ValueError:
    #         pass  # Ignore invalid input
    #
    # status_filter = request.GET.get('status')  # Get the raw string
    #
    # if status_filter:
    #     status_filter = status_filter.split(',')  # Convert it into a list
    #     status_filter = [s.strip() for s in status_filter if s]  # Remove spaces & empty values
    #
    # # Apply status filter
    # if status_filter:
    #     candidates = candidates.filter(candidatestage__stage__name__in=status_filter).distinct()
    #
    # # candidates = candidates.order_by('-updated')
    # paginator = Paginator(candidates, request.GET.get('length', len(candidates)))
    # page = request.GET.get('start', 0)
    # page_number = (int(page) // paginator.per_page) + 1
    # data = []  # Initialize empty list
    #
    # for c in paginator.page(page_number):
    #     status = ', '.join([stage.stage.name for stage in c.candidatestage_set.all()])
    #     data.append(
    #         {
    #             'id': c.id,
    #             'name': c.name,
    #             'designation': c.current_designation,
    #             'email': c.email,
    #             'contact': c.contact,
    #             'location': c.location,
    #             'experience': c.experience,
    #             'status': status,
    #             'updated': c.updated.strftime('%d-%m-%Y %H:%M')
    #         })
    #
    # return JsonResponse({
    #     'draw': int(request.GET.get('draw', 1)),
    #     'recordsTotal': Candidate.objects.filter(company=request.user.employee.company).count(),
    #     'recordsFiltered': candidates.count(),
    #     'data': data
    # })

class CandidateListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/candidate_list.html'
    title = 'Candidate Database'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        # context['candidates'] = Candidate.objects.filter(job_openings__assignemployee=self.request.user.employee, company=self.request.user.employee.company)
        # context['candidates'] = Candidate.objects.filter(company=self.request.user.employee.company).order_by('updated')
        context['job_openings'] = JobOpening.objects.filter(company=self.request.user.employee.company, active=True)

        return context

class ShareJobOpeningView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        ids = request.POST.get('ids[]')  # Get list of IDs from POST data
        job_opening_id = request.POST.get('job_opening_id')

        job_opening = JobOpening.objects.get(id=job_opening_id)
        if ids:
            ids = [int(id) for id in ids.split(',')]
            for id in ids:
                try:
                    candidate = Candidate.objects.get(id=id)
                    site_url = self.request.META.get('HTTP_HOST')  # Get current domain for activation link
                    send_job_opening_email(request.user, candidate, job_opening, site_url)
                except Exception as e:
                    messages.error(self.request, message='There was an error!')
                    return JsonResponse({'status': 'error', 'message': str(e)})

        return JsonResponse({'status': 'success'})

class ResumeListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/resume_list.html'
    title = 'Resume Database'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        # context['candidates'] = Candidate.objects.filter(job_openings__assignemployee=self.request.user.employee, company=self.request.user.employee.company)
        candidates = Candidate.objects.filter(company=self.request.user.employee.company).exclude(upload_resume__isnull=True).exclude(upload_resume="")
        context['candidates'] = candidates.order_by('-updated')
        context['counts'] = f"Total {candidates.count()} resumes"

        context['job_openings'] = JobOpening.objects.filter(company=self.request.user.employee.company, active=True)

        return context


class ResumeSearchView(LoginRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q').strip()
        if query:
            keywords = [word.strip() for word in query.replace(',', ' ').split() if word.strip()]
            query_filter = Q()
            for keyword in keywords:
                query_filter &= Q(text_content__icontains=keyword)
            candidates = Candidate.objects.filter(
                query_filter,
                company=self.request.user.employee.company,
                upload_resume__isnull=False
            ).order_by('-updated')
            counts = f'Filtered {candidates.count()} resumes from {Candidate.objects.filter(company=self.request.user.employee.company).exclude(upload_resume__isnull=True).exclude(upload_resume="").count()}'

        else:
            candidates = Candidate.objects.filter(company=self.request.user.employee.company).exclude(upload_resume__isnull=True).exclude(upload_resume="").order_by('-updated')
            counts = f'Total {candidates.count()} resumes'

        results = []
        for candidate in candidates:
            results.append({
                'id': candidate.id,
                'filename': candidate.filename,
                'resume_url': candidate.upload_resume.url,
                'content': candidate.text_content[:100],  # Limit to 100 characters or customize
                'updated': candidate.updated.strftime('%Y-%m-%d'),  # Customize as needed
            })
        return JsonResponse({'results': results, 'counts': counts})

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
