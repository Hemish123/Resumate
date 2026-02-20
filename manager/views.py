import requests
from django.shortcuts import render,get_object_or_404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin

from dashboard.utils import new_opening_email
from .models import ClientDocument, JobOpening, Client
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
    fields = ['client', 'designation', 'location', 'openings', 'budget', 'job_type', 'job_mode',
              'requiredskills', 'jobdescription', 'assignemployee', 'jd_content', 'min_experience',
              'max_experience', 'education', 'content_type', 'skills_criteria']
    template_name = "manager/job_opening_create.html"
    title = "Job-Opening"
    permission_required = 'manager.add_jobopening'  # Replace with actual permission codename
    success_url = reverse_lazy('job-opening')

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
        # context['clients'] = Client.objects.filter(company=self.request.user.employee.company)
        # context['clients'] = Client.objects.all()
        # context['clients'] = Client.objects.filter(created_by=self.request.user)
        if self.request.user.is_superuser:
            context['clients'] = Client.objects.all()
        else:
            context['clients'] = Client.objects.filter(
                created_by__employee__company=self.request.user.employee.company
            )
        # Load JSON data for designations and skills
        # with open("dashboard/static/dashboard/json/designations.json") as f:
        #     context['data'] = json.load(f)

        with open("dashboard/static/dashboard/json/skills.json") as f:
            context['skills'] = json.load(f)

        return context

    def form_valid(self, form):
        if self.request.POST:
            job_opening = form.save(commit=False)
            # for demo account
            if self.request.user.employee.company.name != "JMS Advisory":
                if len(JobOpening.objects.filter(company=self.request.user.employee.company)) >= 3:
                    form.add_error(None, 'You can not create more than 3 job openings!')
                    return self.form_invalid(form)

        hiring_for = self.request.POST.get("hiring_for")

        # DEFAULT (very important)
        client = None  
        job_opening.company = self.request.user.employee.company

        if hiring_for == "self":
            job_opening.client = None
            job_opening.created_by = self.request.user
            job_opening.save()

            # Default stages
            Stage.objects.create(job_opening_id=job_opening.id, name='Applied', order=1)
            Stage.objects.create(job_opening_id=job_opening.id, name='Sent to Client', order=2)
            Stage.objects.create(job_opening_id=job_opening.id, name='Initial Stage', order=3)
            Stage.objects.create(job_opening_id=job_opening.id, name='Rejected', order=40)
            Stage.objects.create(job_opening_id=job_opening.id, name='Hired', order=50)

            messages.success(self.request, 'Opening created successfully!')
            return redirect('dashboard')   # 🔑 Return is mandatory


        else:
            client = form.cleaned_data.get("client")

            if not client:
                form.add_error("client", "Please select a client")
                return self.form_invalid(form)

            job_opening.client = client
            # job_opening.company = client.company   # ✅ CLIENT MATHI COMPANY
            # job_opening.company = self.request.user.employee.company   # ✅ FIXED

            job_opening.created_by = self.request.user

            designation = form.cleaned_data['designation']
            location = form.cleaned_data['location']
            jd_content = form.cleaned_data['jd_content']
            file = form.cleaned_data['jobdescription']
            employees = form.cleaned_data['assignemployee']
            job_opening.created_by = self.request.user
            
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
                if JobOpening.objects.filter(company=self.request.user.employee.company ,designation=designation, active=True).exists():
                    form.add_error('designation', 'Opening already exists')
                    return self.form_invalid(form)
             
            # Save the job opening and create default stages
            job_opening.save()
            # Assign employees properly to ManyToMany field
            job_opening.assignemployee.set(employees)
            message = "New Job Opening " + job_opening.designation + " assigned to you"
            for e in employees:
                Notification.objects.create(user_id=e.user.id, message=message)
                new_opening_email(job_opening, e)

            if file and not jd_content:
                jd_content = extractText(job_opening.jobdescription.path)
                job_opening.jd_content = jd_content
            Stage.objects.create(job_opening_id=job_opening.id, name='Applied', order=1)
            Stage.objects.create(job_opening_id=job_opening.id, name='Sent to Client', order=2)
            Stage.objects.create(job_opening_id=job_opening.id, name='Initial Stage', order=3)
            Stage.objects.create(job_opening_id=job_opening.id, name='Rejected', order=40)
            Stage.objects.create(job_opening_id=job_opening.id, name='Hired', order=50)

            messages.success(self.request, 'Opening created successfully!')
            # return redirect(reverse('job-opening-generate', kwargs={'pk':job_opening.pk}))
            return redirect('dashboard')
            # return super().form_valid(form)


        
class JobOpeningUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = JobOpening
    fields = ['client', 'designation','location', 'openings', 'budget', 'job_type', 'job_mode',
              'requiredskills', 'jobdescription', 'assignemployee', 'jd_content', 'min_experience',
              'max_experience', 'education', 'content_type', 'skills_criteria', 'active','hiring_for']
    template_name = "manager/job_opening_update.html"
    title = "Job-Opening-Update"
    permission_required = 'manager.change_jobopening'  # Replace with actual permission codename

    def get_success_url(self):
        return reverse_lazy('job-opening')

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='change_jobopening').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['choices'] = Employee.objects.filter(company=self.request.user.employee.company)
        # context['clients'] = Client.objects.all()
        # context['clients'] = Client.objects.filter(created_by=self.request.user)
        if self.request.user.is_superuser:
                context['clients'] = Client.objects.all()
        else:
                context['clients'] = Client.objects.filter(
                    created_by__employee__company=self.request.user.employee.company
                )
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
            hiring_for = self.request.POST.get("hiring_for")
            if hiring_for == "self":
                    job_opening.client = None
                    job_opening.company = self.request.user.employee.company
            else:
                client = form.cleaned_data.get("client")
                if not client:
                    form.add_error("client", "Please select a client")
                    return self.form_invalid(form)
                job_opening.client = client
                job_opening.company = self.request.user.employee.company  # keep your fixed logic

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
    success_url = reverse_lazy('job-opening')
    permission_required = 'manager.delete_jobopening'

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='delete_jobopening').exists()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if "cancel" in request.POST:
                    return redirect(self.success_url)

                # ✅ Allow delete for self
        return super().post(request, *args, **kwargs)

class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    fields = ['name', 'location', 'email', 'contact', 'website']
    template_name = "manager/create_client.html"
    title = "Add New Client"
    permission_required = 'manager.add_client'  # Replace with actual permission codename
    # success_url = 'dashboard/dashboard.html'

    def generate_client_id(self):
            last_client = Client.objects.order_by('-id').first()

            if last_client and last_client.client_id:
                last_id = int(last_client.client_id.replace('CL', ''))
                new_id = last_id + 1
            else:
                new_id = 1

            return f"CL{new_id:04d}"
    
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

        if previous_page and ('job-opening-create' in previous_page):
            self.request.session['previous_page'] = ''
            return reverse_lazy('job-opening')
        return reverse_lazy('job-opening')

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


from django.shortcuts import render, redirect
from .forms import ClientOnboardingForm
from django.contrib import messages

def client_onboarding(request):
    generated_id = generate_client_id()  # always define it

    if request.method == "POST":
        form = ClientOnboardingForm(request.POST,request.FILES)
        if form.is_valid():
            client = form.save(commit=False)
            client.client_id = generate_client_id()
            client.created_by = request.user   # ✅ IMPORTANT
            client.save()
            # Multiple documents save
            for f in request.FILES.getlist('document_upload'):
                ClientDocument.objects.create(client=client, file=f)
           # ---------------- Commercial Terms ----------------

            payment_select = request.POST.get("payment_period_select")
            payment_custom = request.POST.get("payment_period_custom")

            replacement_select = request.POST.get("replacement_period_select")
            replacement_custom = request.POST.get("replacement_period_custom")

            # Payment Period
            if payment_custom:
                client.payment_period = int(payment_custom)
            elif payment_select:
                client.payment_period = int(payment_select)
            else:
                client.payment_period = None

            # Replacement Period
            if replacement_custom:
                client.replacement_period = int(replacement_custom)
            elif replacement_select:
                client.replacement_period = int(replacement_select)
            else:
                client.replacement_period = None

            client.save()


            # ---------------- Hiring POC ----------------
            hiring_names = request.POST.getlist('hiring_name[]')
            hiring_designations = request.POST.getlist('hiring_designation[]')
            hiring_emails = request.POST.getlist('hiring_email[]')
            hiring_contacts = request.POST.getlist('hiring_contact[]')
            hiring_linkedins = request.POST.getlist('hiring_linkedin[]')
            hiring_descriptions = request.POST.getlist('hiring_description[]')

            for i in range(len(hiring_names)):
                if hiring_names[i] and hiring_emails[i]:
                    client.hiring_pocs.create(
                        name=hiring_names[i],
                        designation=hiring_designations[i],
                        email=hiring_emails[i],
                        contact=hiring_contacts[i],
                        linkedin=hiring_linkedins[i],
                        description=hiring_descriptions[i],
                    )
                    # ---------------- Payment POC ----------------
                    payment_names = request.POST.getlist('payment_name[]')
                    payment_designations = request.POST.getlist('payment_designation[]')
                    payment_emails = request.POST.getlist('payment_email[]')
                    payment_contacts = request.POST.getlist('payment_contact[]')
                    payment_linkedins = request.POST.getlist('payment_linkedin[]')
                    payment_descriptions = request.POST.getlist('payment_description[]')

                    for i in range(len(payment_names)):
                        if payment_names[i] and payment_emails[i]:
                            client.payment_pocs.create(
                                name=payment_names[i],
                                designation=payment_designations[i],
                                email=payment_emails[i],
                                contact=payment_contacts[i],
                                linkedin=payment_linkedins[i],
                                description=payment_descriptions[i],
                            )

              # Handle multiple additional emails
            additional_emails = request.POST.getlist('additional_emails')
            from django.core.validators import EmailValidator
            for email in additional_emails:
                email = email.strip()
                if email:
                    try:
                        EmailValidator()(email)
                        client.additional_emails.create(email=email.lower())
                    except Exception:
                        continue  # skip invalid or duplicate emails 
            messages.success(request, "Client successfully onboarded!")
            return redirect('client_list')  # Replace with your client list view
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ClientOnboardingForm()
        generated_id = generate_client_id()

    return render(request, 'manager/client_onboarding.html', {'form': form ,'generated_id': generated_id})

from django.shortcuts import render
from .models import Client
def client_list(request):
    # clients = Client.objects.all()
    if request.user.is_superuser:
        clients = Client.objects.all()
    else:
          clients = Client.objects.filter(
            created_by__employee__company=request.user.employee.company
        )

    print("Clients count:", clients.count())  # <-- add this
    return render(request, 'manager/client_list.html', {'clients': clients})
from django.shortcuts import render, get_object_or_404
from .models import Client, JobOpening   # adjust as per your model name

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)

    # aa client ni badhi openings
    openings = JobOpening.objects.filter(client=client)

    context = {
        "client": client,
        "openings": openings,
    }
    return render(request, "manager/client_detail.html", context)

import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import JobOpening, Client
from dashboard.models import Stage

def job_opening_import(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "Please upload a CSV file.")
            return redirect("job-opening-import")

        if not file.name.endswith(".csv"):
            messages.error(request, "Only CSV files are allowed.")
            return redirect("job-opening-import")

        company = request.user.employee.company
        user_email = request.user.email

        # 🔒 Restriction: Only 3 openings for non-jms accounts
        if not user_email.endswith("@jmsadvisory"):
            existing_count = JobOpening.objects.filter(company=company).count()

            if existing_count >= 3:
                messages.error(request, "You cannot create more than 3 job openings.")
                return redirect("job-opening-import")

        data = file.read().decode("utf-8")
        io_string = io.StringIO(data)
        reader = csv.DictReader(io_string)

        created_count = 0

        for row in reader:

            # 🔒 Check limit inside loop also (important)
            if not user_email.endswith("@jmsadvisory.in"):
                if JobOpening.objects.filter(company=company).count() >= 3:
                    messages.warning(
                        request,
                        "Limit reached. Only 3 job openings allowed for personal accounts."
                    )
                    break
            row = {
                    k.strip().lower().replace(" ", "_"): (v.strip() if v else "")
                    for k, v in row.items()
                }

                # 🚫 Skip completely empty rows
            if not any(row.values()):
                continue
            job = JobOpening.objects.create(
                designation=row.get("designation"),
                location=row.get('location'),
                openings=row.get("openings"),
                budget=row.get("budget"),
                min_experience=row.get("min_exp"),
                max_experience=row.get("max_exp"),
                education=row.get("education"),
                requiredskills=row.get("required_skills"),
                skills_criteria=row.get("skills_criteria(%)"),
                company=company,
                created_by=request.user,
            )

            # Default stages
            Stage.objects.create(job_opening=job, name='Applied', order=1)
            Stage.objects.create(job_opening=job, name='Sent to Client', order=2)
            Stage.objects.create(job_opening=job, name='Initial Stage', order=3)
            Stage.objects.create(job_opening=job, name='Rejected', order=40)
            Stage.objects.create(job_opening=job, name='Hired', order=50)

            created_count += 1

        messages.success(request, f"{created_count} Job Openings imported successfully!")
        return redirect("job-opening")

    return render(request, "manager/job_opening_import.html")


import csv
from django.http import HttpResponse
from .models import Client

def export_clients(request):
    ids = request.GET.get('ids')

    if ids:
        id_list = ids.split(',')
        clients = Client.objects.filter(id__in=id_list)
    else:
        clients = Client.objects.all()  # export all if no ids

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clients_full.csv"'

    writer = csv.writer(response)

    # Header Row
    writer.writerow([
        'ID', 'Name', 'Email', 'Alternative Email', 'Phone', 'Alternative Contact', 'Website',
        'Company', 'Joined', 'Location', 'Client Location', 'Street', 'City', 'State', 'Country', 'Postal Code',
        'LinkedIn', 'Industry', 'GST No', 'Payment Period', 'Replacement Period', 'Status', 'Commercials Decided',
        'Hiring POCs', 'Payment POCs', 'Additional Emails'
    ])

    for index, client in enumerate(clients, start=1):
        # Combine Hiring POCs
        hiring_pocs = "; ".join([
            f"{poc.name} ({poc.designation}) - {poc.email}" for poc in client.hiring_pocs.all()
        ])
        # Combine Payment POCs
        payment_pocs = "; ".join([
            f"{poc.name} ({poc.designation}) - {poc.email}" for poc in client.payment_pocs.all()
        ])
        # Combine Additional Emails
        additional_emails = "; ".join([email.email for email in client.additional_emails.all()])

        writer.writerow([
            index,
            client.name,
            client.email,
            client.alternative_email,
            client.contact,
            client.alternative_contact,
            client.website,
            client.company,
            client.joined.strftime("%d %b %Y") if client.joined else '',
            client.location,
            client.client_location,
            client.street,
            client.city,
            client.state,
            client.country,
            client.postal_code,
            client.linkedin,
            client.industry,
            client.gst_no,
            client.payment_period,
            client.replacement_period,
            client.status,
            client.commercials_decided,
            hiring_pocs,
            payment_pocs,
            additional_emails
        ])

    return response

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Client

def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        client.delete()
        messages.success(request, "Client deleted successfully.")
        return redirect("client_list")

    return redirect("client_list")


from django.shortcuts import render, redirect, get_object_or_404
from .models import Client, HiringPOC, PaymentPOC
from .forms import ClientOnboardingForm


def update_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    files = request.FILES.getlist('document_upload')  # multiple files

    if request.method == "POST":
        form = ClientOnboardingForm(request.POST, request.FILES, instance=client)

        if form.is_valid():
            client = form.save(commit=False)
            client.save()
            for f in files:
                    ClientDocument.objects.create(client=client, file=f)

            # Delete old POCs
            client.hiring_pocs.all().delete()
            client.payment_pocs.all().delete()

            # ---- Hiring POC ----
            hiring_names = request.POST.getlist("hiring_name[]")
            hiring_designations = request.POST.getlist("hiring_designation[]")
            hiring_emails = request.POST.getlist("hiring_email[]")
            hiring_contacts = request.POST.getlist("hiring_contact[]")
            hiring_linkedin = request.POST.getlist("hiring_linkedin[]")
            hiring_description = request.POST.getlist("hiring_description[]")

            for i in range(len(hiring_names)):
                if hiring_names[i] and hiring_emails[i]:
                    HiringPOC.objects.create(
                        client=client,
                        name=hiring_names[i],
                        designation=hiring_designations[i],
                        email=hiring_emails[i],
                        contact=hiring_contacts[i],
                        linkedin=hiring_linkedin[i],
                        description=hiring_description[i],
                    )

            # ---- Payment POC ----
            payment_names = request.POST.getlist("payment_name[]")
            payment_designations = request.POST.getlist("payment_designation[]")
            payment_emails = request.POST.getlist("payment_email[]")
            payment_contacts = request.POST.getlist("payment_contact[]")
            payment_linkedin = request.POST.getlist("payment_linkedin[]")
            payment_description = request.POST.getlist("payment_description[]")

            for i in range(len(payment_names)):
                if payment_names[i] and payment_emails[i]:
                    PaymentPOC.objects.create(
                        client=client,
                        name=payment_names[i],
                        designation=payment_designations[i],
                        email=payment_emails[i],
                        contact=payment_contacts[i],
                        linkedin=payment_linkedin[i],
                        description=payment_description[i],
                    )

            messages.success(request, "Client updated successfully!")
            return redirect("client_list")

    else:
        form = ClientOnboardingForm(instance=client)

    return render(request, "manager/update_client.html", {
        "form": form,
        "client": client,
        "hiring_pocs": client.hiring_pocs.all(),
        "payment_pocs": client.payment_pocs.all(),
        "is_update": True
    })


def generate_client_id():
    last_client = Client.objects.order_by('-id').first()

    if last_client and last_client.client_id:
        last_id = int(last_client.client_id.replace('CL', ''))
        new_id = last_id + 1
    else:
        new_id = 1

    return f"CL{new_id:04d}"

import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Client, HiringPOC, PaymentPOC
from .views import generate_client_id  # if you have separate file


def client_import(request):

    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "Please upload a CSV file.")
            return redirect("client-import")

        if not file.name.endswith(".csv"):
            messages.error(request, "Only CSV files allowed.")
            return redirect("client-import")
        
        file_bytes=file.read()

        try:
            data=file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            data=file_bytes.decode("Latin-1")


        # io_string = io.StringIO(data)
        # reader = csv.DictReader(io_string)
        io_string = io.StringIO(data, newline="")

        reader = csv.DictReader(
            io_string,
            delimiter=",",
            quotechar='"',
            skipinitialspace=True
        )


        created_count = 0
        duplicate_count = 0
        for row in reader:

            try:
                row = {
                    (k.strip().lower().replace(" ", "_") if k else ""):
                    (v.strip() if v else "")
                    for k, v in row.items()
                }

                # Agreement date
                joined_date = timezone.now()
                if row.get("agreement_date"):
                    try:
                        joined_date = datetime.strptime(
                            row.get("agreement_date"),
                            "%d-%m-%Y"
                        )
                    except:
                        pass

                # Safe integer conversion
                try:
                    payment_period = int(row.get("payment_period")) if row.get("payment_period") else None
                except:
                    payment_period = None

                try:
                    replacement_period = int(row.get("replacement_period")) if row.get("replacement_period") else None
                except:
                    replacement_period = None

                # Status safe handling
                status_value = row.get("status", "active").lower()
                if status_value not in ["active", "inactive"]:
                    status_value = "active"

                # Duplicate email skip
                email_value = row.get("email", "").lower()

                if email_value and Client.objects.filter(email=email_value).exists():
                    duplicate_count += 1
                    continue
            
            

                # ---------------- Create Client ----------------
                client = Client.objects.create(
                    client_id=generate_client_id(),
                    created_by=request.user,
                    company=row.get("company", ""),
                    name=row.get("name", ""),
                    email=email_value,
                    alternative_email=row.get("alternative_email", ""),
                    contact=row.get("contact", ""),
                    alternative_contact=row.get("alternative_contact", ""),
                    website=row.get("website", ""),
                    linkedin=row.get("linkedin", ""),
                    location=row.get("location", ""),
                    street=row.get("street", ""),
                    city=row.get("city", ""),
                    state=row.get("state", ""),
                    country=row.get("country", ""),
                    postal_code=row.get("postal_code", ""),
                    client_location=row.get("client_location", ""),
                    industry=row.get("industry", ""),
                    gst_no=row.get("gst_no", ""),
                    payment_period=payment_period,
                    replacement_period=replacement_period,
                    joined=joined_date,
                    status=status_value,
                    commercials_decided=row.get("commercials_decided", ""),
                )


                # ---------------- Hiring POC ----------------
                if row.get("hiring_name") and row.get("hiring_email"):
                    HiringPOC.objects.create(
                        client=client,
                        name=row.get("hiring_name"),
                        designation=row.get("hiring_designation"),
                        email=row.get("hiring_email"),
                        contact=row.get("hiring_contact"),
                        linkedin=row.get("hiring_linkedin"),
                        description=row.get("hiring_description"),
                    )

                # ---------------- Payment POC ----------------
                if row.get("payment_name") and row.get("payment_email"):
                    PaymentPOC.objects.create(
                        client=client,
                        name=row.get("payment_name"),
                        designation=row.get("payment_designation"),
                        email=row.get("payment_email"),
                        contact=row.get("payment_contact"),
                        linkedin=row.get("payment_linkedin"),
                        description=row.get("payment_description"),
                    )

                created_count += 1

            except Exception as e:
                continue


        if created_count > 0:
            messages.success(request, f"{created_count} Clients Imported Successfully!")

        if duplicate_count > 0:
            messages.warning(request, "Clients already existed .")

        # if error_count > 0:
        #     messages.error(request, f"{error_count} Rows had errors and were skipped.")

        # if created_count == 0 and duplicate_count > 0:
        #     messages.info(request, "No new clients were added. All records already exist.")
        return redirect("client_list")

    return render(request, "manager/client_import.html")
