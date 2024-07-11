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
from .serializers import StageSerializer
from django.views.generic.edit import FormView
from django.http import JsonResponse
from .forms import StageForm




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
            context['job_posts'] = JobOpening.objects.all()
        else:
            employee = Employee.objects.get(user=self.request.user)
            try:
                job_posts = JobOpening.objects.filter(assignemployee=employee)

                if job_posts.exists():
                    context['job_posts'] = JobOpening.objects.filter(assignemployee=employee)
                else :
                    context['no_job_posts'] = 'No assigned openings'
            except Employee.DoesNotExist:
                context['no_job_posts'] = 'Nothing'

        return context


class StageAPIView(APIView):
    serializer_class = StageSerializer

    def get(self, request, pk=None):
        job_opening_id = self.kwargs.get('pk')  # Assuming you pass job_opening_id in the URL
        stages = Stage.objects.filter(job_opening_id=job_opening_id).order_by('order')
        if not stages.exists():
            Stage.objects.create(job_opening_id=job_opening_id, name='Initial Stage', order=1)
            stages = self.get_queryset()  # Refresh queryset after creating stage

        serializer = self.serializer_class(stages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the stage
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # def get_queryset(self):
    #     job_opening_id = self.kwargs.get('pk')
    #     return Stage.objects.filter(job_opening_id=job_opening_id).order_by('order')

class StageView(LoginRequiredMixin, TemplateView):

    template_name = 'dashboard/stages.html'
    title = 'Job Process'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StageForm
        job_opening_id = self.kwargs.get('pk')
        job_opening = JobOpening.objects.get(pk=job_opening_id)
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
