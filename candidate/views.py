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


from datetime import datetime

from datetime import datetime

def parse_date_safe(value):
    if not value:
        return None
    
    value = str(value).strip()

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
    ]
    
    for f in formats:
        try:
            return datetime.strptime(value, f).date()
        except:
            continue
    
    return None

def parse_ctc(value):
    if not value:
        return None
    match = re.search(r'\d+(\.\d+)?', str(value))
    return float(match.group()) if match else None 

import re

def extract_number(value):
    if not value:
        return None
    match = re.search(r'\d+(\.\d+)?', str(value))
    return float(match.group()) if match else None

def get_value(row, key):
    for k in row.keys():
        if k.replace(" ", "").lower() == key.replace(" ", "").lower():
            return row[k]
    return None



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

                # for row in sheet.iter_rows(min_row=2, values_only=True):  # Skipping header
                #         name = row[0]
                #         designation = row[1]
                #         contact = row[2]
                #         email = row[3]
                #         location = row[4]  # Unpack first three columns into name, email, contact
                #     if name and ('@' in str(email1).strip()) and (len(str(contact))>=10):   # Check if row is not empty
                #         email = row[2].lower() if isinstance(row[2], str) else None
                #         if email:
                #             if not Candidate.objects.filter(email=email, company=request.user.employee.company).exists():
                #                 try:
                #                     experience = int(row[5])
                #                 except (ValueError, TypeError):
                #                     experience = 0
                #                 #
                #                 # if not row[3]:
                #                 #     row[3] = None
                #                 # if not row[4]:
                #                 #     row[4] = None
                #                 Candidate.objects.create(
                #                     name=row[0],
                #                     contact=row[1],
                #                     email=row[2],
                #                     current_designation=row[3],
                #                     location=row[4],
                #                     experience=experience,
                #                     company=request.user.employee.company
                #                 )
                #             else:
                #                 skip += 1
                #         else:
                #             skip += 1
                #     else:
                #         skip += 1
                for row in sheet.iter_rows(min_row=2, values_only=True):

                    name = row[0]
                    designation = row[1]
                    contact = row[2]
                    email = row[3]
                    location = row[4]

                    if name and email and ('@' in str(email).strip()) and (len(str(contact)) >= 10):

                        email = email.lower()

                        if not Candidate.objects.filter(email=email, company=request.user.employee.company).exists():
                            try:
                                experience = int(row[6]) if len(row) > 6 and row[6] else 0
                            except (ValueError, TypeError):
                                experience = 0

                            Candidate.objects.create(
                                name=name,
                                contact=contact,
                                email=email,
                                current_designation=designation,
                                location=location,
                                experience=experience,
                                company=request.user.employee.company
                            )
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
                # reader = csv.reader(decoded_file)
                # # Skipping the header row (optional)
                # next(reader, None)
                # for row in reader:
                #     email = row[2].lower() if isinstance(row[2], str) else None
                #     if email:
                #         if not Candidate.objects.filter(email=email,
                #                                         company=request.user.employee.company).exists():
                #             try:
                #                 experience = int(row[5])
                #             except (ValueError, TypeError):
                #                 experience = 0

                #             Candidate.objects.create(
                #                 name=row[0],
                #                 contact=row[1],
                #                 email=row[2],
                #                 current_designation=row[3],
                #                 location=row[4],
                #                 experience=experience,
                #                 company=request.user.employee.company
                #             )
                #             # print('candidate')
                #         else:
                #             skip += 1
                #     else:
                #         skip += 1
                reader = csv.DictReader(decoded_file)

                for row in reader:

                    name = row.get("Name")
                    designation = row.get("Designation")
                    contact = row.get("Contact")
                    email = row.get("Email")
                    location = row.get("Location")

                    if email and "@" in str(email):

                        email = email.lower()

                        if not Candidate.objects.filter(email=email, company=request.user.employee.company).exists():

                            Candidate.objects.create(

                                name=get_value(row,"Name"),
                                contact=get_value(row,"Contact"),
                                email=get_value(row,"Email"),
                                current_designation=get_value(row,"Designation"),

                                location=get_value(row,"Location"),
                                preferred_location=get_value(row,"Preferred Location"),

                                experience=int(extract_number(get_value(row,"Experience (In Years)"))) if get_value(row,"Experience (In Years)") else 0,

                                current_ctc=parse_ctc(get_value(row,"Current CTC")),
                                expected_ctc=parse_ctc(get_value(row,"Expected CTC")),

                                notice_period=int(extract_number(get_value(row,"Notice Period"))) if get_value(row,"Notice Period") else None,

                                share_date=parse_date_safe(get_value(row,"Share Date")),

                                dob = parse_date_safe(get_value(row, "DOB")) if get_value(row, "DOB") else None,

                                college = get_value(row, "College"),

                                current_organization=get_value(row,"Current Organization"),

                                company=request.user.employee.company
                            )
                        else:
                            skip += 1
            else:
                messages.error(request, "Invalid file format! Please upload CSV or Excel file.")
                return redirect('candidate-list')
            if skip > 0:
                messages.warning(request, f"{skip} duplicate candidates were skipped during import.")

            messages.success(request, "Candidates imported successfully.")
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
            
            # for local
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
            # email = form.cleaned_data['email'].lower()
            email = form.cleaned_data.get('email')
            if email:
                email = email.lower()
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

            # ================= EMAIL PRIORITY LOGIC =================

            final_email = None

            # 1️⃣ Priority – Form Email
            if email and email.strip():
                final_email = email.strip().lower()

            # 2️⃣ Fallback – Resume Extracted Email
            else:
                resume_text = candidate.text_content
                if resume_text:
                    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                    emails = re.findall(email_pattern, resume_text)
                    if emails:
                        final_email = emails[0].lower()

            if final_email:
                candidate.email = final_email

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

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.conf import settings
import os
from azure.storage.blob import BlobServiceClient

class ResumeListView(LoginRequiredMixin, TemplateView):
    template_name = 'candidate/resume_list.html'
    title = 'Resume Database'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title

        # ================= LOCAL =================
        if settings.DEBUG:
            candidates = Candidate.objects.filter(
                company=self.request.user.employee.company
            ).exclude(
                upload_resume__isnull=True
            ).exclude(
                upload_resume=""
            ).order_by('-updated')

            for candidate in candidates:
                candidate.resume_url = (
                    candidate.upload_resume.url
                    if candidate.upload_resume else None
                )
                # Load extracted text file
                txt_path = os.path.join(
                    settings.MEDIA_ROOT,
                    "resume_text",
                    candidate.upload_resume.name + ".txt"
                )

                if os.path.exists(txt_path):
                    with open(txt_path, "r", encoding="utf-8") as f:
                        candidate.dynamic_content = f.read()[:150]
                else:
                    candidate.dynamic_content = ""

            context['candidates'] = candidates
            context['counts'] = f"Total {candidates.count()} resumes"

        # ================= PRODUCTION (AZURE) =================
        else:
            user_email = self.request.user.email.lower()
            # 🔥 Only allow Azure listing for JMS Advisory
            if user_email.endswith("@jmsadvisory"):
                account_name = os.environ["AZURE_ACCOUNT_NAME"]
                account_key = os.environ["AZURE_ACCOUNT_KEY"]

                connect_str = (
                    f"DefaultEndpointsProtocol=https;"
                    f"AccountName={account_name};"
                    f"AccountKey={account_key};"
                    f"EndpointSuffix=core.windows.net"
                )

                blob_service_client = BlobServiceClient.from_connection_string(connect_str)
                container_client = blob_service_client.get_container_client("media")

                blobs = container_client.list_blobs(name_starts_with="resumes/")

                resume_list = []

                for blob in blobs:

                    filename = blob.name.split("/")[-1]

                    file_url = f"https://{account_name}.blob.core.windows.net/media/{blob.name}"

                    candidate = Candidate.objects.filter(
                        upload_resume=blob.name
                    ).first()

                    content_preview = ""

                    # ✅ If already saved in DB
                    if candidate and candidate.text_content:
                        content_preview = candidate.text_content[:120]

                    # ✅ If not saved → Extract from Azure once
                    elif candidate:
                        extracted_text = get_blob_pdf_text(blob.name)

                        if extracted_text:
                            candidate.text_content = extracted_text
                            candidate.save(update_fields=["text_content"])

                            content_preview = extracted_text[:120]

                    resume_list.append({
                        "name": filename,
                        "resume_url": file_url,
                        "updated": blob.last_modified,
                        "content": content_preview
                    })
                    

                context['candidates'] = resume_list
                context['counts'] = f"Total {len(resume_list)} resumes"
            else:
                    # ❌ Other companies should NOT see Azure resumes
                    context['candidates'] = []
                    context['counts'] = "Total 0 resumes"

        context['job_openings'] = JobOpening.objects.filter(
            company=self.request.user.employee.company,
            active=True
        )

        return context


from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import os

from adminuser.utils import extract_resume_text
from .models import Candidate


class ResumeUploadView(LoginRequiredMixin, View):
    

    def post(self, request):
        resume_file = request.FILES.get("resume")

        # ✅ 1. Check file exists FIRST
        if not resume_file:
            messages.error(request, "Please select a file.")
            return redirect("resume-list")

        # ✅ 2. Validate extension BEFORE saving
        allowed_extensions = ['.pdf', '.doc', '.docx']
        ext = os.path.splitext(resume_file.name)[1].lower()

        if ext not in allowed_extensions:
            messages.error(request, "Only PDF, DOC, DOCX files allowed.")
            return redirect("resume-list")

        # ✅ 3. Extract text safely
        try:
            extracted_text = extract_resume_text(resume_file)
        except Exception as e:
            messages.error(request, "Error extracting resume content.")
            return redirect("resume-list")

        # IMPORTANT: reset file pointer after reading
        resume_file.seek(0)

        # ✅ 4. Save candidate ONLY ONCE
        candidate = Candidate.objects.create(
            company=request.user.employee.company,
            name=os.path.splitext(resume_file.name)[0],
            upload_resume=resume_file,
            text_content=extracted_text
        )

        # ✅ 5. Save extracted text as .txt file
        txt_folder = os.path.join(settings.MEDIA_ROOT, "resume_text")
        os.makedirs(txt_folder, exist_ok=True)

        txt_filename = candidate.upload_resume.name.replace("/", "_") + ".txt"
        txt_path = os.path.join(txt_folder, txt_filename)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(extracted_text or "")

        messages.success(request, "Resume uploaded and content extracted successfully!")
        return redirect("resume-list")
    

# from django.http import JsonResponse
# from django.core.paginator import Paginator
# from django.db.models import Q


# def resume_list_api(request):
#     draw = int(request.GET.get("draw", 1))
#     start = int(request.GET.get("start", 0))
#     length = int(request.GET.get("length", 10))

#    # Base queryset (IMPORTANT - company based filter)
#     candidates = Candidate.objects.filter(
#         company=request.user.employee.company
#     ).exclude(
#         upload_resume__isnull=True
#     ).exclude(
#         upload_resume=""
#     )

#     # ----------- Filters (Same as your original logic) ------------

#     name = request.GET.get("name")
#     if name:
#         candidates = candidates.filter(name__icontains=name)

#     filename = request.GET.get("filename")
#     if filename:
#         candidates = candidates.filter(filename__icontains=filename)

#     designation = request.GET.get("designation")
#     if designation:
#         candidates = candidates.filter(current_designation__icontains=designation)

#     experience = request.GET.get("experience")
#     if experience:
#         candidates = candidates.filter(experience__gte=experience)

#     education = request.GET.get("education")
#     if education:
#         candidates = candidates.filter(education__icontains=education)

#     location = request.GET.get("location")
#     if location:
#         candidates = candidates.filter(location__icontains=location)

#     skill = request.GET.get("skill")
#     if skill:
#         candidates = candidates.filter(text_content__icontains=skill)

#     industry = request.GET.get("industry")
#     if industry:
#         candidates = candidates.filter(text_content__icontains=industry)

#     # Order
#     candidates = candidates.order_by("-updated")

#     # ------------ DataTable Pagination -------------

#     total_records = Candidate.objects.filter(
#         company=request.user.employee.company
#     ).exclude(
#         upload_resume__isnull=True
#     ).exclude(
#         upload_resume=""
#     ).count()

#     filtered_records = candidates.count()

#     paginator = Paginator(candidates, length)
#     page_number = (start // length) + 1
#     page = paginator.get_page(page_number)

#     data = []

#     for candidate in page:
#         data.append({
#             "id": candidate.id,
#             "filename": candidate.filename,
#             "file_url": candidate.upload_resume.url if candidate.upload_resume else "",
#             "content": candidate.text_content[:120] if candidate.text_content else "",
#             "updated": candidate.updated.strftime("%d-%m-%Y"),
#             # "name": candidate.name,
#             # "designation": candidate.current_designation,
#             # "experience": candidate.experience,
#             # "education": candidate.education,
#             # "location": candidate.location,
#             # "updated": candidate.updated.strftime("%d-%m-%Y"),
#         })

#     return JsonResponse({
#         "draw": draw,
#         "recordsTotal": total_records,
#         "recordsFiltered": filtered_records,
#         "data": data,
#     })
from django.http import JsonResponse
from django.conf import settings
from azure.storage.blob import BlobServiceClient
import os


def resume_list_api(request):

    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    data = []
    # GET filter params for both DEBUG and PRODUCTION
    filename = request.GET.get("filename", "").strip()
    updated = request.GET.get("updated", "").strip()

    # ================= LOCAL =================

    if settings.DEBUG:

        candidates = Candidate.objects.filter(
            company=request.user.employee.company
        ).exclude(
            upload_resume__isnull=True
        ).exclude(
            upload_resume=""
        ).order_by("-updated")

        total_records = candidates.count()

          # -------- INDIVIDUAL FILTERS --------

        # name = request.GET.get("name", "").strip()
        # if name:
        #     candidates = candidates.filter(name__icontains=name)

        filename = request.GET.get("filename", "").strip()
        if filename:
            candidates = candidates.filter(filename__icontains=filename)

        updated = request.GET.get("updated", "").strip()
        if updated:
            candidates = candidates.filter(updated__date=updated)

        # designation = request.GET.get("designation", "").strip()
        # if designation:
        #     candidates = candidates.filter(current_designation__icontains=designation)

        # experience = request.GET.get("experience", "").strip()
        # if experience:
        #     candidates = candidates.filter(experience__gte=experience)

        # education = request.GET.get("education", "").strip()
        # if education:
        #     candidates = candidates.filter(education__icontains=education)

        # location = request.GET.get("location", "").strip()
        # if location:
        #     candidates = candidates.filter(location__icontains=location)

        # ---------------- SKILLS FILTER (Multi-keyword AND) ----------------

        # skills = request.GET.get("skills", "").strip()

        # if skills:
        #     skill_keywords = skills.replace(",", " ").split()

        #     for skill in skill_keywords:
        #         candidates = candidates.filter(
        #             text_content__icontains=skill
        #         )


        filtered_records = candidates.count()
        candidates = candidates.order_by("-updated")
        page = candidates[start:start+length]

        for candidate in page:

            data.append({
                "id": candidate.id,
                "filename": candidate.upload_resume.name.split("/")[-1],
                "file_url": candidate.upload_resume.url,
                "content": candidate.text_content[:120] if candidate.text_content else "",
                "updated": candidate.updated.strftime("%d-%m-%Y"),
            })

    # ================= PRODUCTION =================

    else:

        account_name = os.environ["AZURE_ACCOUNT_NAME"]
        account_key = os.environ["AZURE_ACCOUNT_KEY"]

        connect_str = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account_name};"
            f"AccountKey={account_key};"
            f"EndpointSuffix=core.windows.net"
        )

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        container_client = blob_service_client.get_container_client("media")

        blobs = list(container_client.list_blobs(name_starts_with="resumes/"))

        # TOTAL COUNT
        total_records = len(blobs)

         # FILTER filename
        if filename:
            blobs = [
                b for b in blobs
                if filename.lower() in b.name.lower()
            ]

        # FILTER updated
        if updated:
            blobs = [
                b for b in blobs
                if b.last_modified.date().strftime("%Y-%m-%d") == updated
            ]

        filtered_records = len(blobs)

        # SORT
        blobs.sort(key=lambda x: x.last_modified, reverse=True)

        # PAGINATION
        blobs = blobs[start:start+length]

        for blob in blobs:

            filename = blob.name.split("/")[-1]

            file_url = f"https://{account_name}.blob.core.windows.net/media/{blob.name}"
            candidate = Candidate.objects.filter(
                upload_resume=blob.name
            ).first()

            content_preview = ""

            if candidate and candidate.text_content:
                content_preview = candidate.text_content[:120]


            data.append({
                "id": blob.name,
                "filename": filename,
                "file_url": file_url,
                "content": content_preview,
                "updated": blob.last_modified.strftime("%d-%m-%Y"),
            })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data,
    })

from django.conf import settings
from azure.storage.blob import BlobServiceClient
import os
from django.db.models import Q
from django.http import JsonResponse


class ResumeSearchView(LoginRequiredMixin, APIView):

    def get(self, request, *args, **kwargs):

        query = request.GET.get('q', '').strip()

        # ================= LOCAL =================
        if settings.DEBUG:

            candidates = Candidate.objects.filter(
                company=request.user.employee.company
            ).exclude(
                upload_resume__isnull=True
            ).exclude(
                upload_resume=""
            )

            if query:
                keywords = query.replace(',', ' ').split()
                for keyword in keywords:
                    candidates = candidates.filter(
                        text_content__icontains=keyword
                    )

            candidates = candidates.order_by('-updated')

            results = []
            for candidate in candidates:
                results.append({
                    "id": candidate.id,
                    "filename": candidate.filename,
                    "resume_url": candidate.upload_resume.url,
                    "content": candidate.text_content[:100] if candidate.text_content else "",
                    "updated": candidate.updated.strftime('%Y-%m-%d')
                })

            return JsonResponse({
                "results": results,
                "counts": f"Total {candidates.count()} resumes"
            })

        # ================= PRODUCTION (AZURE) =================
        else:

            account_name = os.environ["AZURE_ACCOUNT_NAME"]
            account_key = os.environ["AZURE_ACCOUNT_KEY"]

            connect_str = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={account_name};"
                f"AccountKey={account_key};"
                f"EndpointSuffix=core.windows.net"
            )

            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            container_client = blob_service_client.get_container_client("media")

            blobs = container_client.list_blobs(name_starts_with="resumes/")

            resume_list = []

            for blob in blobs:
                filename = blob.name.split("/")[-1]

                # 🔎 search in filename (Azure does not have text_content)
                if query and query.lower() not in filename.lower():
                    continue

                file_url = f"https://{account_name}.blob.core.windows.net/media/{blob.name}"

                resume_list.append({
                    "id": blob.name,
                    "filename": filename,
                    "resume_url": file_url,
                    "content": "",
                    "updated": blob.last_modified.strftime('%Y-%m-%d')
                })

            return JsonResponse({
                "results": resume_list,
                "counts": f"Total {len(resume_list)} resumes"
            })
# class ResumeSearchView(LoginRequiredMixin, APIView):
#     def get(self, request, *args, **kwargs):
#         query = request.GET.get('q').strip()
#         if query:
#             keywords = [word.strip() for word in query.replace(',', ' ').split() if word.strip()]
#             query_filter = Q()
#             for keyword in keywords:
#                 query_filter &= Q(text_content__icontains=keyword)
#             candidates = Candidate.objects.filter(
#                 query_filter,
#                 company=self.request.user.employee.company,
#                 upload_resume__isnull=False
#             ).order_by('-updated')
#             counts = f'Filtered {candidates.count()} resumes from {Candidate.objects.filter(company=self.request.user.employee.company).exclude(upload_resume__isnull=True).exclude(upload_resume="").count()}'

#         else:
#             candidates = Candidate.objects.filter(company=self.request.user.employee.company).exclude(upload_resume__isnull=True).exclude(upload_resume="").order_by('-updated')
#             counts = f'Total {candidates.count()} resumes'

#         results = []
#         for candidate in candidates:
#             results.append({
#                 'id': candidate.id,
#                 'filename': candidate.filename,
#                 'resume_url': candidate.upload_resume.url,
#                 'content': candidate.text_content[:100],  # Limit to 100 characters or customize
#                 'updated': candidate.updated.strftime('%Y-%m-%d'),  # Customize as needed
#             })
#         return JsonResponse({'results': results, 'counts': counts})
    
# from django.views import View
# from django.shortcuts import render
# from django.contrib.auth.mixins import LoginRequiredMixin

# class ResumeFilterView(LoginRequiredMixin, View):

#     def get(self, request):

#         candidates = Candidate.objects.filter(
#             company=request.user.employee.company
#         ).exclude(
#             upload_resume__isnull=True
#         ).exclude(upload_resume="")

#         # Candidate Name
#         name = request.GET.get('name')
#         if name:
#             candidates = candidates.filter(name__icontains=name)

#         # File Name
#         filename = request.GET.get('filename')
#         if filename:
#             candidates = candidates.filter(filename__icontains=filename)

#         # Designation
#         designation = request.GET.get('designation')
#         if designation:
#             candidates = candidates.filter(current_designation__icontains=designation)

#         # Experience
#         experience = request.GET.get('experience')
#         if experience:
#             candidates = candidates.filter(experience__gte=experience)

#         # Education
#         education = request.GET.get('education')
#         if education:
#             candidates = candidates.filter(education__icontains=education)

#         # Location
#         location = request.GET.get('location')
#         if location:
#             candidates = candidates.filter(location__icontains=location)

#         # Skill
#         skill = request.GET.get('skill')
#         if skill:
#             candidates = candidates.filter(text_content__icontains=skill)

#         # Industry
#         industry = request.GET.get('industry')
#         if industry:
#             candidates = candidates.filter(text_content__icontains=industry)

#         candidates = candidates.order_by('-updated')

#         return render(request, "candidate/resume_list.html", {
#             "candidates": candidates,
#             "counts": candidates.count()
#         })



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


import requests
import tempfile
from django.core.files.base import ContentFile
from .extract_text import extract_text_from_pdf  # tamaru existing function

from urllib.parse import quote
import requests
import io
from PyPDF2 import PdfReader

from urllib.parse import quote
import requests
import io
from PyPDF2 import PdfReader

def get_blob_pdf_text(blob_name):
    try:
        # Proper URL encode
        encoded_name = quote(blob_name.split("/")[-1])

        blob_url = f"{settings.MEDIA_URL}resumes/{encoded_name}"

        response = requests.get(blob_url)
        if response.status_code != 200:
            return ""

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        return text

    except Exception as e:
        print("Blob Parsing Error:", e)
        return ""

import requests
import tempfile
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .models import Candidate
from .extract_text import extract_text_from_pdf

import requests
import tempfile
import os
import io
from urllib.parse import unquote
from PyPDF2 import PdfReader
from docx import Document
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import Candidate


def save_candidate_from_blob_url(request):
    if request.method == "GET":
        return render(request, "candidate/blob_test.html")

    blob_url = request.POST.get("resume_url")

    if not blob_url:
        return HttpResponse("No URL provided")

    response = requests.get(blob_url)

    if response.status_code != 200:
        return HttpResponse("Failed to download file")

    # Clean filename properly
    filename = unquote(blob_url.split("/")[-1])
    file_extension = os.path.splitext(filename)[1].lower()

    file_bytes = response.content

    # 🔍 Validate real file content
    if file_bytes.startswith(b'%PDF'):
        file_type = "pdf"
    elif file_bytes.startswith(b'PK'):
        file_type = "docx"
    else:
        return HttpResponse("Invalid or corrupted file in Azure")

    extracted_text = ""

    # ================= PDF =================
    if file_type == "pdf":
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            extracted_text += page.extract_text() or ""

    # ================= DOCX =================
    elif file_type == "docx":
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)
        for para in doc.paragraphs:
            extracted_text += para.text + "\n"

    # ================= SAVE TO DB =================
    candidate = Candidate.objects.create(
        company=request.user.employee.company,
        name=filename.replace(file_extension, ""),
        upload_resume=ContentFile(file_bytes, name=filename),
        text_content=extracted_text
    )

    return redirect("resume-list")