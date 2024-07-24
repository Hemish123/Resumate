from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from manager.models import JobOpening
from users.models import Employee
from .models import Stage, CandidateStage
from candidate.models import Candidate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Stage, CandidateStage
from .serializers import StageSerializer, CandidateSerializer
from django.views.generic.edit import FormView
from django.http import JsonResponse
from .forms import StageForm
from django.db.models import Max
import json




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

        if self.request.user.is_superuser or self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            context['job_posts'] = JobOpening.objects.all().order_by('-active')
        else:
            employee = Employee.objects.get(user=self.request.user)
            try:
                job_posts = JobOpening.objects.filter(assignemployee=employee).order_by('-active')

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
        candidates = Candidate.objects.all()
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
            order = Stage.objects.filter(job_opening_id=job_opening_id).exclude(name='Hired').aggregate(Max('order'))['order__max'] or 0
            stage = Stage.objects.create(id=stageid, name=stage_name, job_opening=job_opening, order=order+1)
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

        print('or' , order)
        if stage_id:
            stage = Stage.objects.get(id=stage_id)
            for item in order:
                candidate_stage_id = item.get('id')
                candidate_order = item.get('order')
                CandidateStage.objects.filter(id=candidate_stage_id).update(order=candidate_order, stage=stage)
        else:
            for item in order[:-1]:
                stage_id = item.get('id')
                if Stage.objects.filter(id=stage_id).name == 'Hired' :
                    continue
                print('s', stage_id)
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
            stage.delete()
        if candidateid:
            stage = Stage.objects.get(job_opening=job_opening, id=candidatestageid)
            candidate = CandidateStage.objects.get(stage=stage, id=candidateid)
            candidate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StageView(LoginRequiredMixin, TemplateView):

    template_name = 'dashboard/stages.html'
    title = 'Job Process'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StageForm
        job_opening_id = self.kwargs.get('pk')
        job_opening = JobOpening.objects.get(pk=job_opening_id)
        with open("dashboard/static/dashboard/json/skills.json") as f:
            skills = json.load(f)
        context['skills'] = skills
        context['s_skills'] = job_opening.requiredskills.split(',')
        context['active'] = job_opening.active
        print('s', context['s_skills'])
        stages = Stage.objects.filter(job_opening=job_opening).order_by('order')
        candidates_by_stage = {}
        if Stage.objects.filter(job_opening=job_opening).exists():
            for stage in stages:
                candidates = Candidate.objects.filter(
                    candidatestage__stage=stage,

                ).order_by('candidatestage__order')
                candidates_by_stage[stage.name] = candidates

        context['job_opening'] = job_opening
        # context['stages'] = stages
        context['candidates_by_stage'] = candidates_by_stage
        return context



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
