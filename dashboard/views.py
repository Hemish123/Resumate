from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from future.backports.datetime import datetime
from django.utils import timezone
import pytz
from manager.models import JobOpening
from users.models import Employee
from .models import Stage, CandidateStage
from candidate.models import Candidate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Stage, CandidateStage, Event
from .serializers import StageSerializer, CandidateSerializer
from django.views.generic.edit import FormView
from django.http import JsonResponse
from .forms import StageForm
from django.db.models import Max
import json
from django.utils.dateformat import DateFormat
from collections import defaultdict



class DashbaordView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    title = 'Dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['user'] = self.request.user
        # Access permission details (optional)
        has_perm = self.request.user.groups.filter(permissions__codename='add_jobopening').exists()
        context['has_perm'] = has_perm
        self.request.session['previous_page'] = ''

        if self.request.user.is_superuser:
            job_posts = JobOpening.objects.all().order_by('-active')

            if job_posts.exists():
                context['job_posts'] = job_posts
            else:
                context['no_job_posts'] = 'No openings'
        elif self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            job_posts = JobOpening.objects.filter(company=self.request.user.employee.company).order_by('-active')
            if job_posts.exists():
                context['job_posts'] = job_posts
            else:
                context['no_job_posts'] = 'No openings'
        else:
            employee = Employee.objects.get(user=self.request.user)

            try:
                job_posts = JobOpening.objects.filter(company=employee.company, assignemployee=employee).order_by('-active')

                if job_posts.exists():
                    context['job_posts'] = job_posts
                else :
                    context['no_job_posts'] = 'No assigned openings'
            except Employee.DoesNotExist:
                context['no_job_posts'] = 'Nothing'

        return context


class CandidateAPIView(APIView):
    serializer_class = CandidateSerializer

    def get(self, request):
        job_opening_id = request.GET.get('jobOpeningId')
        candidates = Candidate.objects.filter(company=request.user.employee.company, job_openings__id=job_opening_id)
        if not candidates.exists():
            return Response({'detail': 'No candidates found.'}, status=status.HTTP_200_OK)

        serializer = self.serializer_class(candidates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StageAPIView(APIView):
    serializer_class = StageSerializer

    def get(self, request, pk=None):
        job_opening_id = self.kwargs.get('pk')  # Assuming you pass job_opening_id in the URL
        stages = Stage.objects.filter(job_opening_id=job_opening_id).order_by('order')
        if not stages.exists():
            Stage.objects.create(job_opening_id=job_opening_id, name='Initial Stage', order=1)
            Stage.objects.create(job_opening_id=job_opening_id, name='Hired', order=10)
            stages = Stage.objects.filter(job_opening_id=job_opening_id).order_by('order')  # Refresh queryset after creating stage

        serializer = self.serializer_class(stages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        job_opening_id = self.kwargs.get('pk')
        # serializer = self.serializer_class(data=request.data)
        # print('s : ', serializer )
        job_opening = JobOpening.objects.get(id=job_opening_id)
        # stage_instance = serializer.save()  # Save the stage
        candidateid = request.data.get('candidateid')
        stageid = request.data.get('id')
        stage_name = request.data.get('title')
        if stage_name:
            order = Stage.objects.filter(job_opening_id=job_opening_id).exclude(name__in=['Hired', 'Rejected']).aggregate(Max('order'))['order__max'] or 0
            stage = Stage.objects.create(name=stage_name, job_opening=job_opening, order=order+1)
            stage.save()
        if candidateid:
            stage = Stage.objects.get(id=stageid)
            order = CandidateStage.objects.filter(stage_id=stageid).aggregate(Max('order'))['order__max'] or 0
            candidate = Candidate.objects.get(id=candidateid)
            candidate.job_openings.add(job_opening)
            candidate_stage = CandidateStage(stage=stage, candidate=candidate, order=order+1)
            candidate_stage.save()

        serializer = self.serializer_class(stage)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        order = request.data.get('order', [])
        stage_id = request.data.get('stage_id')

        if stage_id:
            stage = Stage.objects.get(id=stage_id)
            for item in order:
                candidate_stage_id = item.get('id')
                candidate_order = item.get('order')
                CandidateStage.objects.filter(id=candidate_stage_id).update(order=candidate_order, stage=stage)
        else:
            for item in order[:-1]:
                stage_id = item.get('id')
                stage_name = Stage.objects.get(id=stage_id)
                if stage_name.name == 'Hired' :
                    continue
                order = item.get('order')
                Stage.objects.filter(id=stage_id).update(order=order)

        return JsonResponse({'status': 'success'}, status=200)

    def delete(self, request, pk):

        stageid = request.data.get('stage_id')
        candidateid = request.data.get('candidate_id')
        candidatestageid = request.data.get('candidate_stage_id')
        job_opening = JobOpening.objects.get(id=pk)
        if stageid:
            stage = Stage.objects.get(job_opening=job_opening, id=stageid)
            if (stage.name != 'Initial Stage') and (stage.name != 'Hired') and (stage.name != 'Applied') and (stage.name != 'Rejected'):
                stage.delete()
        if candidateid:
            stage = Stage.objects.get(job_opening=job_opening, id=candidatestageid)
            candidate = CandidateStage.objects.get(stage=stage, id=candidateid)
            Candidate.objects.get(id=candidate.candidate.id).job_openings.remove(job_opening)
            candidate.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class StageView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/stages.html'
    title = 'Job Process'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the JobOpening instance
        job_opening_id = self.kwargs.get('pk')
        job_opening = get_object_or_404(JobOpening, pk=job_opening_id)
        
        context['s_skills'] = job_opening.requiredskills
       
        context['active'] = job_opening.active

        # Retrieve stages and candidates
        stages = Stage.objects.filter(job_opening=job_opening).order_by('order')
        context['stages'] = stages


        # Add data to the context
        context['job_opening'] = job_opening
        print('employee', job_opening.assignemployee.all())


        # Add job description and job details to the context
        if job_opening.content_type == 'file' and job_opening.jobdescription:
            context['job_description_file'] = job_opening.jobdescription
        elif job_opening.content_type == 'text' and job_opening.jd_content:
            context['job_description_text'] = job_opening.jd_content

        context['job_type'] = job_opening.job_type
        context['job_mode'] = job_opening.job_mode

        return context

    def post(self, request, *args, **kwargs):

        stage_id = request.POST.get('stage')
        candidate_stage_id = request.POST.get('candidateStageId')
        print('s', stage_id, candidate_stage_id)
        order = CandidateStage.objects.filter(stage_id=stage_id).aggregate(Max('order'))['order__max'] or 0

        # stageid = request.data.get('stage_id')
        CandidateStage.objects.filter(id=candidate_stage_id).update(order=order+1, stage_id=stage_id)
        return HttpResponseRedirect(reverse('job-process', kwargs={'pk': self.kwargs['pk']}))


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidates'] = Candidate.objects.filter(company=self.request.user.employee.company)
        context['designation'] = JobOpening.objects.filter(company=self.request.user.employee.company)
        events = Event.objects.filter(company=self.request.user.employee.company).order_by('start_datetime')
        # Create a nested dictionary to group events by year and month
        grouped_events = {}

        for event in events:
            year = event.start_datetime.year
            month = DateFormat(event.start_datetime).format('F')  # Get full month name
            date = event.start_datetime.date()
            if date < datetime.today().date():
                continue
            # Check if the year already exists in the dictionary
            if year not in grouped_events:
                grouped_events[year] = {}  # Initialize the year as a dictionary

            # Check if the month already exists for the given year
            if month not in grouped_events[year]:
                grouped_events[year][month] = []  # Initialize the month as a list

            grouped_events[year][month].append(event)
        context['upcoming'] = grouped_events
        # [print('d', e.start_datetime) for e in events]

        # Create a list of dictionaries to store event data
        event_data = [
            {
                "id": event.id,
                "title": event.title,
                "start": event.start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                "end": event.end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                "extendedProps": {
                    "candidate": event.candidate.name,
                    "jobopening_id": event.designation.id,
                    "designation": event.designation.designation,
                    "candidate_id": event.candidate.id,
                    "interviewer": event.interviewer,
                    "interview_type": event.interview_type,
                    "interview_url": event.interview_url,
                    "date": event.start_datetime.strftime('%Y-%m-%d'),
                    "start_time": event.start_datetime.strftime('%H:%M:%S'),
                    "end_time": event.end_datetime.strftime('%H:%M:%S'),
                    "description": event.description,
                    "location": event.location
                }
            }

            for event in events
        ]

        # Convert the list of events to a JSON string
        context['events'] = json.dumps(event_data)
        return context


    def post(self, request, *args, **kwargs):
        # Parse the incoming JSON data
        data = json.loads(request.body)

        # Extract fields from the JSON data
        id = data.get('id')
        title = data.get('title')
        candidate_id = data.get('candidate')
        candidate = Candidate.objects.get(id=candidate_id)
        jobopening_id = data.get('designation')
        designation = JobOpening.objects.get(id=jobopening_id)
        interviewer = data.get('interviewer')
        date_str = data.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time_str = data.get('start_time')
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time_str = data.get('end_time')
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        description = data.get('description')
        location = data.get('location')
        interview_type = data.get('interview_type')
        interview_url = data.get('interview_url')
        start_datetime = datetime.combine(date,start_time)
        end_datetime = datetime.combine(date, end_time)

        # Process and save the data to the database (e.g., creating an event)
        # Assuming you have an Event model (example shown)\
        if id:
            event = Event.objects.get(id=id)
            event.title = title
            event.candidate = candidate
            event.interviewer = interviewer
            event.interview_url = interview_url
            event.start_datetime = start_datetime
            event.end_datetime = end_datetime
            event.description = description
            event.location = location
            event.interview_type = interview_type
            event.designation = designation
            event.save()
        else:
            event = Event.objects.create(
                title=title,
                candidate=candidate,
                interviewer=interviewer,
                interview_url=interview_url,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                description=description,
                location=location,
                interview_type=interview_type,
                designation=designation,
                company=request.user.employee.company
            )
        event_data = {
                "id": event.id,
                "title": event.title,
                "start": event.start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                "end": event.end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                "extendedProps": {
                    "candidate": event.candidate.name,
                    "candidate_id": event.candidate.id,
                    "jobopening_id": event.designation.id,
                    "designation": event.designation.designation,
                    "interviewer": event.interviewer,
                    "interview_type": event.interview_type,
                    "interview_url": event.interview_url,
                    "date": event.start_datetime.strftime('%Y-%m-%d'),
                    "start_time": event.start_datetime.strftime('%H:%M:%S'),
                    "end_time": event.end_datetime.strftime('%H:%M:%S'),
                    "description": event.description,
                    "location": event.location
                }
            }
        # Return a success response
        return JsonResponse({'status': 'success', 'event_data': event_data})

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)
        id = data.get('id')
        event = Event.objects.get(id=id)
        event.delete()
        return JsonResponse({'status': 'success'})






# class ContactUsView(FormView):
#     template_name = 'screening/contactus.html'
#     form_class = ContactForm
#     success_url = '/contactus/'  # Adjust this as needed
#
#     def form_valid(self, form):
#         name = form.cleaned_data['name']
#         email = form.cleaned_data['email']
#         message = form.cleaned_data['message']
#
#         # Send email
#         send_mail(
#             'New Contact Us Submission',
#             f'Name: {name}\nEmail: {email}\nMessage: {message}',
#             settings.DEFAULT_FROM_EMAIL,
#             ['resumate1nfo1@gmail.com'],
#             fail_silently=False,
#         )
#
#         return JsonResponse({'success': True})
#
#     def form_invalid(self, form):
#         return JsonResponse({'success': False, 'errors': form.errors}, status=400)
