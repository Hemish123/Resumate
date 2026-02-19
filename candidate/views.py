from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.views.generic import CreateView, TemplateView, DetailView, UpdateView, FormView,View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.signals import post_save
from rest_framework.views import APIView
from django.core.paginator import Paginator
from django.db.models import Q, Subquery, OuterRef, Value
from django.db.models.functions import Coalesce
from dashboard.models import CandidateStage, Stage
from .models import Candidate, ResumeAnalysis
from users.models import Employee
from manager.models import JobOpening
from datetime import datetime, timedelta

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
import tempfile
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
                            # print('candidate')
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
            #for production
            # Download from Azure and write to a local file
            # Define a temporary local path
            local_temp_path = f"/tmp/{resume_file.name}"
            print("path:",local_temp_path)

            with open(local_temp_path, "wb") as f:
                f.write(default_storage.open(path).read())
            
            #for local
            # temp_dir = tempfile.gettempdir()
            # local_temp_path = os.path.join(temp_dir, resume_file.name)

            # with open(local_temp_path, "wb") as f:
            #     f.write(default_storage.open(path).read())


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
                candidate.preferred_location = form.cleaned_data.get('preferred_location')
                candidate.current_ctc = form.cleaned_data.get('current_ctc')
                candidate.expected_ctc = form.cleaned_data.get('expected_ctc')
                candidate.notice_period = form.cleaned_data.get('notice_period')
                candidate.share_date = form.cleaned_data.get('share_date')
                candidate.dob = form.cleaned_data.get('dob')
                candidate.college = form.cleaned_data.get('college')
                candidate.client = job_opening.client
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
    fields = ['name', 'email', 'contact', 'location', 'dob', 'college','linkedin', 'github',
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



    # search_value = request.GET.get('search[value]', '').strip()
    # experience_filter = request.GET.get('experience', '').strip()
    # status_filter = request.GET.get('status', '').strip()
    # start = int(request.GET.get('start', 0))
    # length = int(request.GET.get('length', 10))
    # draw = int(request.GET.get('draw', 1))
    #
    # # Sorting
    # order_column_index = request.GET.get('order[0][column]', '9')
    # order_dir = request.GET.get('order[0][dir]', 'desc')
    # column_mapping = {
    #     "1": "id",
    #     "2": "name",
    #     "3": "current_designation",
    #     "4": "contact",
    #     "5": "email",
    #     "6": "location",
    #     "7": "experience",
    #     "9": "updated",
    # }
    # sort_field = column_mapping.get(order_column_index, 'updated')
    # if order_dir == 'desc':
    #     sort_field = f"-{sort_field}"
    #
    # # Prefetch related CandidateStage objects
    # candidatestage_queryset = Prefetch(
    #     'candidatestage_set',
    #     queryset=CandidateStage.objects.select_related('stage').only('stage__name')
    # )
    #
    # # Base QuerySet
    # base_queryset = Candidate.objects.filter(company=request.user.employee.company).prefetch_related(candidatestage_queryset).only(
    #     'id', 'name', 'current_designation', 'email', 'contact',
    #     'location', 'experience', 'updated', 'company_id'
    # ).order_by(sort_field)
    #
    # total_records = base_queryset.count()
    #
    # # Apply filters
    # filters = Q()
    #
    # if search_value:
    #     keywords = [word.strip() for word in search_value.replace(',', ' ').split()]
    #     for keyword in keywords:
    #         filters &= (
    #             Q(name__icontains=keyword) |
    #             Q(email__icontains=keyword) |
    #             Q(contact__icontains=keyword) |
    #             Q(location__icontains=keyword) |
    #             Q(current_designation__icontains=keyword)
    #         )
    #
    # if experience_filter:
    #     try:
    #         if experience_filter.isdigit():
    #             filters &= Q(experience=int(experience_filter))
    #         else:
    #             comparator, exp_value = experience_filter.split()
    #             exp_value = float(exp_value)
    #             if comparator == '<':
    #                 filters &= Q(experience__lt=exp_value)
    #             elif comparator == '>':
    #                 filters &= Q(experience__gt=exp_value)
    #             elif comparator == '=':
    #                 filters &= Q(experience=exp_value)
    #     except ValueError:
    #         pass
    #
    # if status_filter:
    #     status_list = [s.strip() for s in status_filter.split(',') if s.strip()]
    #     filters &= Q(candidatestage__stage__name__in=status_list)
    #
    # filtered_queryset = base_queryset.filter(filters).distinct()
    # records_filtered = filtered_queryset.count()
    #
    # # Slice QuerySet (pagination)
    # candidates = filtered_queryset[start:start + length]
    #
    # # Build data
    # data = []
    # print('can', len(candidates))
    # for c in candidates:
    #     # Create the 'status' string by joining all related stages
    #     status = ', '.join([stage.stage.name for stage in c.candidatestage_set.all()])
    #     data.append({
    #         'id': c.id,
    #         'name': c.name,
    #         'designation': c.current_designation,
    #         'email': c.email,
    #         'contact': c.contact,
    #         'location': c.location,
    #         'experience': c.experience,
    #         'status': status or '',
    #         'updated': c.updated.strftime('%d-%m-%Y %H:%M')
    #     })
    #
    # return JsonResponse({
    #     'draw': draw,
    #     'recordsTotal': total_records,
    #     'recordsFiltered': records_filtered,
    #     'data': data
    # })\
    from django.db.models import OuterRef, Subquery

def candidate_list_api(request):
    candidates = Candidate.objects.all()
    preferred_location = request.GET.get('preferred_location')
    current_ctc = request.GET.get('current_ctc')
    expected_ctc = request.GET.get('expected_ctc')
    notice_period = request.GET.get('notice_period')
    updated_range = request.GET.get("updated_range")
    from_month = request.GET.get("from_month")
    to_month = request.GET.get("to_month")
    share_from = request.GET.get('share_from')
    share_to = request.GET.get('share_to')
    search_value = request.GET.get('search[value]', '').strip()
    experience_filter = request.GET.get('experience', '').strip()
    status_filter = request.GET.get('status', '').strip()
    location_filter = request.GET.get('location', '').strip()       
    designation_filter = request.GET.get('designation', '').strip() 
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    draw = int(request.GET.get('draw', 1))
    name_filter = request.GET.get('name', '').strip()
    contact_filter = request.GET.get('contact', '').strip()
    email_filter = request.GET.get('email', '').strip()
    updated_filter = request.GET.get('updated', '').strip()
    dob_filter = request.GET.get('dob', '').strip()
    college_filter = request.GET.get('college', '').strip()
    client_filter = request.GET.get('client', '').strip()
    organization_filter = request.GET.get('organization', '').strip()

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
        "7": "preferred_location",
        "8": "experience",
         "9": "current_ctc",
        "10": "expected_ctc",
        "11": "notice_period",
        "12": "share_date",
        "14": "updated",
        "15"   :"dob",
        "16": "college",
        "17": "job_openings__client__name",
        "18": "current_organization",
    }
    sort_field = column_mapping.get(order_column_index, 'updated')
    if order_dir == 'desc':
        sort_field = f"-{sort_field}"

    # Subquery to get the latest stage name
    latest_stage_subquery = CandidateStage.objects.filter(
        candidate=OuterRef('pk')
    ).order_by('-id').values('stage__name')[:1]
  

    queryset = Candidate.objects.filter(
    company=request.user.employee.company
).prefetch_related(
    'job_openings__client'
).annotate(
    stage_name=Coalesce(Subquery(latest_stage_subquery), Value(''))
).only(
    'id', 'name', 'current_designation', 'email', 'contact',
    'location', 'preferred_location', 'experience',
    'dob', 'college', 'client__name','current_organization',
    'current_ctc', 'expected_ctc', 'notice_period',
    'share_date', 'updated', 'company_id'
).order_by(sort_field)
    today = timezone.now().date()

    if updated_range and updated_range.isdigit():
        queryset = queryset.filter(
            updated__date__gte=today - timedelta(days=int(updated_range))
        )

    elif updated_range == "month":
        queryset = queryset.filter(
            updated__year=today.year,
            updated__month=today.month
        )

    elif updated_range == "between" and from_month and to_month:
        from_date = datetime.strptime(from_month, "%Y-%m").date().replace(day=1)

        to_date = datetime.strptime(to_month, "%Y-%m").date()
        if to_date.month == 12:
            to_date = to_date.replace(year=to_date.year + 1, month=1, day=1)
        else:
            to_date = to_date.replace(month=to_date.month + 1, day=1)

        queryset = queryset.filter(
            updated__date__gte=from_date,
            updated__date__lt=to_date
        )

    elif updated_range == "year":
        queryset = queryset.filter(
            updated__date__lte=today - timedelta(days=365)
        )

    total_records = queryset.count()

    # Apply filters
    filters = Q()
    # NAME
    if name_filter:
        filters &= build_multi_icontains('name', name_filter)

    # CONTACT
    if contact_filter:
        filters &= build_multi_icontains('contact', contact_filter )

    # EMAIL
    if email_filter:
        filters &= build_multi_icontains('email', email_filter)

    # UPDATED (DATE)
    if updated_filter:
        dates = [d.strip() for d in updated_filter.split(',') if d.strip()]
        filters &= Q(updated__date__in=dates)

    if preferred_location:
        filters &= build_multi_icontains('preferred_location',preferred_location)

    if current_ctc:
        filters &= build_multi_icontains('current_ctc',current_ctc)

    if expected_ctc:
        filters &= build_multi_icontains('expected_ctc',expected_ctc)

    if notice_period:
        filters &= build_multi_icontains('notice_period',notice_period)

    if share_from:
        try:
            share_from = datetime.strptime(share_from, "%Y-%m-%d").date()
        except ValueError:
            share_from = None

    if share_to:
        try:
            share_to = datetime.strptime(share_to, "%Y-%m-%d").date()
        except ValueError:
            share_to = None

    if share_from and share_to:
        filters &= Q(share_date__range=[share_from, share_to])

    elif share_from:
        filters &= Q(share_date__gte=share_from)

    elif share_to:
        filters &= Q(share_date__lte=share_to)


    if dob_filter:
        filters &= Q(dob=dob_filter)

    if college_filter:
        filters &= build_multi_icontains('college', college_filter)

    if client_filter:
        filters &= Q(client__name__icontains=client_filter)

    if organization_filter:
        filters &= build_multi_icontains('current_organization', organization_filter)

    # if search_value:
    #     keywords = [word.strip() for word in search_value.replace(',', ' ').split()]
    #     for keyword in keywords:
    #         filters &= (
    #                 Q(name__icontains=keyword) |
    #                 Q(email__icontains=keyword) |
    #                 Q(contact__icontains=keyword) |
    #                 Q(location__icontains=keyword) |
    #                 Q(current_designation__icontains=keyword)
    #         )
    if search_value:
        # Convert "ahmedabad,surat" → ["ahmedabad", "surat"]
        keywords = [word.strip() for word in search_value.replace(",", " ").split() if word.strip()]

        search_query = Q()

        # OR logic between keywords
        for keyword in keywords:
            search_query |= (
                Q(name__icontains=keyword) |
                Q(email__icontains=keyword) |
                Q(contact__icontains=keyword) |
                Q(location__icontains=keyword) |
                Q(current_designation__icontains=keyword)
            )

        filters &= search_query
            
    if location_filter:
        filters &= build_multi_icontains('location', location_filter)
    if designation_filter:
        filters &= build_multi_icontains('current_designation',designation_filter)

    min_exp = request.GET.get('min_exp', '').strip()
    max_exp = request.GET.get('max_exp', '').strip()

    # Filter using min & max experience
    if min_exp.isdigit() and max_exp.isdigit():
        filters &= Q(experience__gte=int(min_exp), experience__lte=int(max_exp))

    elif min_exp.isdigit():
        filters &= Q(experience__gte=int(min_exp))

    elif max_exp.isdigit():
        filters &= Q(experience__lte=int(max_exp))

    if status_filter:
        status_filters = Q()
        status_list = [s.strip() for s in status_filter.split(',') if s.strip()]

        if "In Stage" in status_list:
            exclude_stages = ['']
            if "Hired" not in status_list:
                exclude_stages.append("Hired")
            if "Rejected" not in status_list:
                exclude_stages.append("Rejected")

            # Exclude these stages (including empty string if needed)
            status_filters |= ~Q(stage_name__in=exclude_stages)

        # Add direct matches for other statuses (except "In Stage" and "Inactive")
        direct_statuses = [s for s in status_list if s not in ["In Stage", "Inactive"]]
        if direct_statuses:
            status_filters |= Q(stage_name__in=direct_statuses)

        if 'Inactive' in status_list:
            status_filters |= Q(stage_name='')
        else:
            status_filters &= Q(job_openings__active=True)
        filters &= status_filters

    filtered_queryset = queryset.filter(filters)

    # Apply pagination
    paginator = Paginator(filtered_queryset, length)
    page_number = start // length + 1
    page = paginator.get_page(page_number)
    candidates = list(page.object_list)

    # Build data
    data = []
    for c in candidates:
        if not c.job_openings.filter(active=True).exists():
            c.stage_name = ''  # or 'Inactive' if that's what you want
        data.append({
            'id': c.id,
            'name': c.name,
            'designation': c.current_designation,
            'email': c.email,
            'contact': c.contact,
            'location': c.location,
            'preferred_location': c.preferred_location,
            'experience': c.experience,
            'dob': c.dob.strftime('%d-%m-%Y') if c.dob else '',
            'college': c.college or '',
            'client': (
                c.job_openings.first().client.name
                if c.job_openings.exists() and c.job_openings.first().client
                else ''
            ),

            'current_organization': c.current_organization or '',
            'current_ctc': c.current_ctc,
            'expected_ctc': c.expected_ctc,
            'notice_period': c.notice_period,
            'share_date': c.share_date.strftime('%d-%m-%Y') if c.share_date else '',
            'status': c.stage_name or '',
            'updated': c.updated.strftime('%d-%m-%Y %H:%M')
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': paginator.count,
        'data': data
    })

    import csv
from django.http import HttpResponse
from .models import Candidate   # adjust model name

# def export_selected_candidates_csv(request):
#     ids = request.GET.get('ids', '')

#     if not ids:
#         return HttpResponse("No candidates selected", status=400)

#     id_list = ids.split(',')

#     candidates = Candidate.objects.filter(id__in=id_list)

#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="selected_candidates.csv"'

#     writer = csv.writer(response)

#     # CSV HEADER
#     writer.writerow([
#         'Name',
#         'Designation',
#         'Contact',
#         'Email',
#         'Location',
#         'Experience',
#         'Status',
#         'Updated On'
#     ])

#     # CSV ROWS
#     for c in candidates:
#         writer.writerow([
#             c.name,
#             c.current_designation,
#             c.contact,
#             c.email,
#             c.location,
#             c.experience,
#             c.get_status(),
#             c.updated.strftime('%Y-%m-%d %H:%M')
#         ])

#     return response

import csv
from django.http import HttpResponse
from django.utils.timezone import localtime

def export_selected_candidates_csv(request):
    ids = request.GET.get('ids', '')

    if not ids:
        return HttpResponse("No candidates selected", status=400)

    id_list = ids.split(',')

    candidates = Candidate.objects.filter(
        id__in=id_list
    ).select_related('client')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="selected_candidates.csv"'

    writer = csv.writer(response)

    # ✅ HEADER (Same as Table)
    writer.writerow([
        'Name',
        'Designation',
        'Contact',
        'Email',
        'Location',
        'Preferred Location',
        'Experience (In Years)',
        'Current CTC',
        'Expected CTC',
        'Notice Period',
        'Share Date',
        'Status',
        'Updated',
        'DOB',
        'College',
        'Client',
        'Current Organization'
    ])

    # ✅ ROWS
    for c in candidates:
        writer.writerow([
            c.name,
            c.current_designation or '',
            c.contact,
            c.email,
            c.location or '',
            c.preferred_location or '',
            c.experience,
            c.current_ctc,
            c.expected_ctc,
            c.notice_period,
            c.share_date.strftime('%Y-%m-%d') if c.share_date else '',
            c.get_status(),
            localtime(c.updated).strftime('%Y-%m-%d %H:%M'),
            c.dob.strftime('%Y-%m-%d') if c.dob else '',
            c.college or '',
            c.client.name if c.client else '',
            c.current_organization or ''
        ])

    return response

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

# class ShareJobOpeningView(LoginRequiredMixin, View):

#     def post(self, request, *args, **kwargs):

#         ids_json = request.POST.get("ids")
#         job_opening_id = request.POST.get("job_opening_id")

#         if not ids_json:
#             return JsonResponse({"status": "error", "message": "No candidates selected"})

#         try:
#             ids = json.loads(ids_json)
#         except:
#             return JsonResponse({"status": "error", "message": "Invalid ID format"})

#         job_opening = JobOpening.objects.get(id=job_opening_id)
#         site_url = request.META.get("HTTP_HOST")

#         for candidate_id in ids:
#             try:
#                 candidate = Candidate.objects.get(id=candidate_id)
#                 send_job_opening_email(request.user, candidate, job_opening, site_url)
#             except Exception as e:
#                 return JsonResponse({"status": "error", "message": str(e)})

#         return JsonResponse({"status": "success"})

class ShareJobOpeningView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        ids_json = request.POST.get("ids")
        job_opening_id = request.POST.get("job_opening_id")

        if not ids_json or not job_opening_id:
            return JsonResponse({
                "status": "error",
                "message": "Missing data"
            })

        try:
            ids = json.loads(ids_json)
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid ID format"
            })

        try:
            job_opening = JobOpening.objects.get(id=job_opening_id)
        except JobOpening.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Job opening not found"
            })

        site_url = request.get_host()

        for candidate_id in ids:
            try:
                candidate = Candidate.objects.get(id=candidate_id)
                send_job_opening_email(
                    request.user,
                    candidate,
                    job_opening,
                    site_url
                )
            except Candidate.DoesNotExist:
                continue   # skip invalid candidate
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": str(e)
                })

        return JsonResponse({"status": "success"})

from django.core.paginator import Paginator

class ResumeListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/resume_list.html'
    title = 'Resume Database'
    paginate_by = 1  # per page resumes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title

        candidates = Candidate.objects.filter(
            company=self.request.user.employee.company
        ).exclude(
            upload_resume__isnull=True
        ).exclude(
            upload_resume=""
        ).order_by('-updated')

        paginator = Paginator(candidates, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['candidates'] = page_obj
        context['page_obj'] = page_obj
        context['counts'] = f"Total {paginator.count} resumes"
        context['job_openings'] = JobOpening.objects.filter(
            company=self.request.user.employee.company,
            active=True
        )

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
    
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

class ResumeFilterView(LoginRequiredMixin, View):

    def get(self, request):

        candidates = Candidate.objects.filter(
            company=request.user.employee.company
        ).exclude(
            upload_resume__isnull=True
        ).exclude(upload_resume="")

        # Candidate Name
        name = request.GET.get('name')
        if name:
            candidates = candidates.filter(name__icontains=name)

        # File Name
        filename = request.GET.get('filename')
        if filename:
            candidates = candidates.filter(filename__icontains=filename)

        # Designation
        designation = request.GET.get('designation')
        if designation:
            candidates = candidates.filter(current_designation__icontains=designation)

        # Experience
        experience = request.GET.get('experience')
        if experience:
            candidates = candidates.filter(experience__gte=experience)

        # Education
        education = request.GET.get('education')
        if education:
            candidates = candidates.filter(education__icontains=education)

        # Location
        location = request.GET.get('location')
        if location:
            candidates = candidates.filter(location__icontains=location)

        # Skill
        skill = request.GET.get('skill')
        if skill:
            candidates = candidates.filter(text_content__icontains=skill)

        # Industry
        industry = request.GET.get('industry')
        if industry:
            candidates = candidates.filter(text_content__icontains=industry)

        candidates = candidates.order_by('-updated')

        return render(request, "candidate/resume_list.html", {
            "candidates": candidates,
            "counts": candidates.count()
        })



class ApplicationListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/application_list.html'
    title = 'All Applications'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        id = self.kwargs.get('pk')
        job_opening = JobOpening.objects.get(pk=id)
        candidates = Candidate.objects.filter(job_openings=job_opening,
                                              company=self.request.user.employee.company
                                              ).order_by('-is_new')
        stages = Stage.objects.get(job_opening_id=id, name='Applied')
        # print("st", stages.id)
        stage = CandidateStage.objects.filter(stage=stages, candidate=OuterRef('pk')).values('stage__name')
        candidates = candidates.annotate(stage=Subquery(stage))
        # for c in candidates:
        #
        #     print("can", c.candidatestage_set.filter(stage=stages).values('stage__id'))
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

        ids_str = request.POST.get('ids')  # "1,2,3"

        if not ids_str:
            return JsonResponse({
                'status': 'error',
                'message': 'No candidates selected'
            })

        try:
            ids = [int(i) for i in ids_str.split(',')]
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid ID format'
            })

        Candidate.objects.filter(id__in=ids).delete()

        return JsonResponse({'status': 'success'})

# class CandidateDeleteView(LoginRequiredMixin, TemplateView):
#     def post(self, request, *args, **kwargs):
        
#         ids = request.POST.get('ids[]')  # Get list of IDs from POST data

#         if ids:
#             ids = [int(id) for id in ids.split(',')]
#             Candidate.objects.filter(id__in=ids).delete()  # Delete candidates with these IDs
#         return JsonResponse({'status': 'success'})

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

        # ✅ New logic: check if candidate has interview answers for this job opening
        has_interview = candidate.interview_answers.filter(job_opening=job_opening).exists()
        context['has_interview'] = has_interview

        return context


def build_multi_icontains(field, value):
    values = [v.strip() for v in value.replace(',', ' ').split() if v.strip()]
    q = Q()
    for v in values:
        q |= Q(**{f"{field}__icontains": v})
    return q
