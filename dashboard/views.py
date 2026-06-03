from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from future.backports.datetime import datetime
from django.utils import timezone
import pytz
from manager.models import JobOpening
from users.models import Employee
from .models import Stage, CandidateStage,InterviewInvitation
from candidate.models import Candidate, ResumeAnalysis
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
from .microsoft_graph_api import get_access_token
from .microsoft_graph_api import create_teams_meeting  # Assuming your helper functions are in utils.py
from .utils import send_hired_email, send_rejected_email, send_stage_change_email, send_interview_email, \
    send_schedule_interview_email,send_interview_invitation_email
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils import send_stage_to_client_email


def email_action(request, candidate_id, action):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if action == "approve":
        print("approved")
        # candidate.status = "approved"
    elif action == "reject":
        print("rejected")
        # candidate.status = "rejected"
    else:
        return JsonResponse({"error": "Invalid action"}, status=400)

    # candidate.save()
    return JsonResponse({"success": f"Candidate {action}d successfully."})

import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from candidate.models import Candidate, ResumeAnalysis
from manager.models import JobOpening
from dashboard.models import Stage
from dashboard.models import CandidateStage, Event
from users.models import Employee
from django.db.models import Count, Avg, Q


class AnalyticsHelper:
    """Helper methods for calculating analytics metrics"""

    @staticmethod
    def get_average_time_to_hire(active_jobs):
        

        try:

            hired_stages = CandidateStage.objects.filter(
                stage__job_opening__in=active_jobs,
                stage__name='Hired'
            )

            durations = []

            for hired in hired_stages:

                first_stage = CandidateStage.objects.filter(
                    candidate=hired.candidate,
                    stage__job_opening=hired.stage.job_opening
                ).order_by('moved_at').first()

                if first_stage:

                    diff = (
                        hired.moved_at -
                        first_stage.moved_at
                    ).days

                    if diff >= 0:
                        durations.append(diff)

            avg_days = (
                round(sum(durations) / len(durations))
                if durations else 0
            )

            return {
                'average_days': avg_days,
                'total_hires_measured': len(durations)
            }

        except Exception as e:
            print("TIME TO HIRE ERROR:", e)

            return {
                'average_days': 0,
                'total_hires_measured': 0
            }

    @staticmethod
    def get_monthly_hiring_trend(active_jobs, months=6):
        """Get hired candidates per month for last N months"""
        try:
            today = timezone.now()
            months_data = []

            for i in range(months, 0, -1):
                month_start = today - timedelta(days=30 * i)
                month_end = today - timedelta(days=30 * (i - 1))

                hired_count = CandidateStage.objects.filter(
                    stage__job_opening__in=active_jobs,
                    stage__name='Hired',
                    moved_at__gte=month_start,
                    moved_at__lte=month_end
                ).count()

                pipeline_count = CandidateStage.objects.filter(
                    stage__job_opening__in=active_jobs,
                    moved_at__gte=month_start,
                    moved_at__lte=month_end
                ).exclude(stage__name='Rejected').count()

                month_label = month_start.strftime('%b')
                months_data.append({
                    'month': month_label,
                    'hired': hired_count,
                    'in_pipeline': pipeline_count
                })

            return months_data
        except Exception as e:
            return []

    @staticmethod
    def get_pipeline_funnel(active_jobs):
        """Get candidate count at each stage"""
        try:
            stages = Stage.objects.filter(
                job_opening__in=active_jobs
            ).distinct().values('name').annotate(count=Count('candidatestage')).order_by('order')

            total_candidates = sum([s['count'] for s in stages])

            funnel_data = []
            for stage in stages:
                percentage = round((stage['count'] / total_candidates) * 100) if total_candidates > 0 else 0
                funnel_data.append({
                    'stage_name': stage['name'],
                    'count': stage['count'],
                    'percentage': percentage
                })

            return funnel_data
        except Exception as e:
            return []

    @staticmethod
    def get_ai_match_score_distribution(active_jobs):
        """Parse ResumeAnalysis JSON and extract skills_matching score"""
        try:
            analyses = ResumeAnalysis.objects.filter(
                job_opening__in=active_jobs
            ).values('response_text')

            score_buckets = {
                '0-25': 0,
                '26-50': 0,
                '51-75': 0,
                '76-100': 0
            }

            all_scores = []
            for analysis in analyses:
                try:
                    response_json = json.loads(analysis['response_text'])
                    match_score = response_json.get('skills_matching', {}).get('match', 0)
                    all_scores.append(match_score)

                    if 0 <= match_score <= 25:
                        score_buckets['0-25'] += 1
                    elif 26 <= match_score <= 50:
                        score_buckets['26-50'] += 1
                    elif 51 <= match_score <= 75:
                        score_buckets['51-75'] += 1
                    elif 76 <= match_score <= 100:
                        score_buckets['76-100'] += 1
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue

            avg_score = round(sum(all_scores) / len(all_scores)) if all_scores else 0
            total_analyzed = sum(score_buckets.values())

            return {
                'score_distribution': score_buckets,
                'total_analyzed': total_analyzed,
                'average_score': avg_score
            }
        except Exception as e:
            return {'score_distribution': {'0-25': 0, '26-50': 0, '51-75': 0, '76-100': 0}, 'total_analyzed': 0, 'average_score': 0}

    @staticmethod
    def get_interview_type_breakdown(active_jobs):
        """Get interview count by type"""
        try:
            interview_counts = Event.objects.filter(
    designation__in=active_jobs

            ).values('interview_type').annotate(count=Count('id')).order_by('-count')

            total_interviews = sum([e['count'] for e in interview_counts])

            breakdown = []
            interview_type_labels = {
                'facetoface': 'Face-to-face',
                'virtual': 'Virtual',
                'telephonic': 'Telephonic'
            }

            for interview in interview_counts:
                interview_type = interview['interview_type'] or 'Unknown'
                label = interview_type_labels.get(interview_type, interview_type)
                percentage = round((interview['count'] / total_interviews) * 100) if total_interviews > 0 else 0

                breakdown.append({
                    'type': label,
                    'count': interview['count'],
                    'percentage': percentage
                })

            return breakdown
        except Exception as e:
            return []

    @staticmethod
    def get_recruiter_performance(active_jobs):
        try:

            recruiters = Employee.objects.filter(
                jobopening__in=active_jobs
            ).distinct().annotate(

                total_jobs=Count(
                    'jobopening',
                    distinct=True
                ),

                hired_count=Count(
                    'jobopening__stage__candidatestage__candidate',
                    filter=Q(
                        jobopening__stage__name='Hired'
                    ),
                    distinct=True
                )

            ).order_by('-hired_count')

            performance_data = []

            for recruiter in recruiters:

                performance_data.append({
                    'name': recruiter.name or recruiter.user.username,
                    'hired': recruiter.hired_count,
                    'total_jobs': recruiter.total_jobs,
                    'initials': ''.join(
                        word[0].upper()
                        for word in (
                            recruiter.name or recruiter.user.username
                        ).split()
                    )
                })

            return performance_data

        except Exception as e:
            print("RECRUITER ERROR:", e)
            return []

    @staticmethod
    def get_ctc_analysis(active_jobs):
        """Get CTC statistics for candidates in these jobs"""
        try:
            candidates = Candidate.objects.filter(
                job_openings__in=active_jobs
            ).distinct(
            ).filter(
                current_ctc__isnull=False,
                expected_ctc__isnull=False
            ).distinct()

            avg_current = candidates.aggregate(avg=Avg('current_ctc'))['avg'] or 0
            avg_expected = candidates.aggregate(avg=Avg('expected_ctc'))['avg'] or 0
            avg_offer = candidates.filter(offer_in_hand__isnull=False).aggregate(avg=Avg('offer_in_hand'))['avg'] or 0

            ctc_gap = round(float(avg_expected - avg_current), 2) if avg_expected and avg_current else 0
            percentage_hike = round(((float(avg_expected) - float(avg_current)) / float(avg_current)) * 100, 1) if avg_current > 0 else 0

            return {
                'average_current_ctc': round(float(avg_current), 1),
                'average_expected_ctc': round(float(avg_expected), 1),
                'average_offer_in_hand': round(float(avg_offer), 1),
                'ctc_gap': ctc_gap,
                'percentage_hike_expected': percentage_hike,
                'candidates_analyzed': candidates.count()
            }
        except Exception as e:
            return {
                'average_current_ctc': 0,
                'average_expected_ctc': 0,
                'average_offer_in_hand': 0,
                'ctc_gap': 0,
                'percentage_hike_expected': 0,
                'candidates_analyzed': 0
            }

    @staticmethod
    def get_notice_period_distribution(active_jobs):
        """Get notice period distribution for candidates"""
        try:
            candidates = Candidate.objects.filter(
                        job_openings__in=active_jobs
                    ).distinct()
            notice_buckets = {
                'immediate': candidates.filter(notice_period=0).count(),
                '1_30_days': candidates.filter(notice_period__gt=0, notice_period__lte=30).count(),
                '31_60_days': candidates.filter(notice_period__gt=30, notice_period__lte=60).count(),
                '60_plus_days': candidates.filter(notice_period__gt=60).count()
            }

            total = sum(notice_buckets.values())

            notice_data = []
            bucket_labels = {
                'immediate': 'Immediate',
                '1_30_days': '1–30 days',
                '31_60_days': '31–60 days',
                '60_plus_days': '60+ days'
            }

            for bucket_key, count in notice_buckets.items():
                percentage = round((count / total) * 100) if total > 0 else 0
                notice_data.append({
                    'bucket': bucket_labels[bucket_key],
                    'count': count,
                    'percentage': percentage
                })

            return notice_data
        except Exception as e:
            return []

    @staticmethod
    def get_top_candidate_locations(active_jobs, limit=10):
        """Get top candidate locations"""
        try:
            top_locations = Candidate.objects.filter(
    job_openings__in=active_jobs,
    location__isnull=False

            ).exclude(location='').distinct().values('location').annotate(
                count=Count('id')
            ).order_by('-count')[:limit]

            locations_data = []
            for loc in top_locations:
                locations_data.append({
                    'location': loc['location'],
                    'count': loc['count']
                })

            return locations_data
        except Exception as e:
            return []


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    title = 'Dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title

        # ============ EXISTING LOGIC (UNCHANGED) ============
        if self.request.user.is_superuser:
            active_jobs = JobOpening.objects.filter(active=True)
            recent_openings = active_jobs.order_by('-updated_on')[:4]
        elif self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            active_jobs = JobOpening.objects.filter(company=self.request.user.employee.company, active=True)
            recent_openings = active_jobs.order_by('-updated_on')[:4]
        else:
            employee = Employee.objects.get(user=self.request.user)
            active_jobs = JobOpening.objects.filter(company=employee.company, assignemployee=employee, active=True)
            recent_openings = active_jobs.order_by('-updated_on')[:4]

        filtered_jobs = []
        for job in active_jobs:
            job.request = self.request
            if not job.is_expired:
                filtered_jobs.append(job)
        active_jobs = filtered_jobs
        active_jobs_count = len(active_jobs)

        candidate_applied = 0
        candidates_hired = 0
        candidates_in_review = 0
        for job in active_jobs:
            candidate_applied += job.candidate_set.count()
            stage = Stage.objects.filter(name='Hired', job_opening=job).first()
            candidates_hired += CandidateStage.objects.filter(stage=stage).count()
            stage_all = Stage.objects.filter(job_opening=job).exclude(name__in=['Hired', 'Rejected'])
            candidates_in_review += CandidateStage.objects.filter(stage__in=stage_all).count()

        context['active_jobs'] = active_jobs_count
        context['candidates_applied'] = candidate_applied
        context['candidates_hired'] = candidates_hired
        context['candidates_in_review'] = candidates_in_review
        context['recent_openings'] = recent_openings

        # ============ NEW ANALYTICS (ADDED) ============
        try:
            # Convert filtered_jobs list to QuerySet for analytics queries
            active_jobs_queryset = JobOpening.objects.filter(pk__in=[j.pk for j in active_jobs])

            # Get all analytics
            time_to_hire = AnalyticsHelper.get_average_time_to_hire(active_jobs_queryset)
            monthly_trend = AnalyticsHelper.get_monthly_hiring_trend(active_jobs_queryset, months=6)
            pipeline = AnalyticsHelper.get_pipeline_funnel(active_jobs_queryset)
            ai_scores = AnalyticsHelper.get_ai_match_score_distribution(active_jobs_queryset)
            interviews = AnalyticsHelper.get_interview_type_breakdown(active_jobs_queryset)
            recruiters = AnalyticsHelper.get_recruiter_performance(active_jobs_queryset)
            ctc = AnalyticsHelper.get_ctc_analysis(active_jobs_queryset)
            notice = AnalyticsHelper.get_notice_period_distribution(active_jobs_queryset)
            locations = AnalyticsHelper.get_top_candidate_locations(active_jobs_queryset)

            print("TIME TO HIRE RESULT =", time_to_hire)
            # Add to context
            context['time_to_hire'] = time_to_hire
            context['monthly_trend'] = json.dumps(monthly_trend)
            context['pipeline'] = pipeline
            context['ai_scores'] = ai_scores
            context['score_0_25'] = ai_scores['score_distribution'].get('0-25', 0)
            context['score_26_50'] = ai_scores['score_distribution'].get('26-50', 0)
            context['score_51_75'] = ai_scores['score_distribution'].get('51-75', 0)
            context['score_76_100'] = ai_scores['score_distribution'].get('76-100', 0)
            context['interviews'] = json.dumps(interviews)
            context['recruiters'] = recruiters
            context['ctc'] = ctc
            context['notice_period'] = notice
            context['locations'] = locations
            

        except Exception as e:
            # Graceful fallback if analytics fail
            print(f"Analytics error: {str(e)}")
            context['time_to_hire'] = {'average_days': 0, 'total_hires_measured': 0}
            context['monthly_trend'] = '[]'
            context['pipeline'] = []
            context['score_0_25'] = ai_scores['score_distribution'].get('0-25', 0)
            context['score_26_50'] = ai_scores['score_distribution'].get('26-50', 0)
            context['score_51_75'] = ai_scores['score_distribution'].get('51-75', 0)
            context['score_76_100'] = ai_scores['score_distribution'].get('76-100', 0)

            context['ai_scores'] = ai_scores
            context['interviews'] = '[]'
            context['recruiters'] = []
            context['ctc'] = {}
            context['notice_period'] = []
            context['locations'] = []

        return context
# class HomeView(LoginRequiredMixin, TemplateView):
#     template_name = 'dashboard/home.html'
#     title = 'Dashboard'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = self.title

#         if self.request.user.is_superuser:
#             active_jobs = JobOpening.objects.filter(active=True)
#             # Fetch recent job openings
#             recent_openings = active_jobs.order_by('-updated_on')[:4]
#         elif self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
#             active_jobs = JobOpening.objects.filter(company=self.request.user.employee.company, active=True)
#             # Fetch recent job openings
#             recent_openings = active_jobs.order_by('-updated_on')[:4]
#         else:
#             employee = Employee.objects.get(user=self.request.user)
#             active_jobs = JobOpening.objects.filter(company=employee.company, assignemployee=employee, active=True)
#             # Fetch recent job openings
#             recent_openings = active_jobs.order_by('-updated_on')[:4]
#         filtered_jobs = []
#         for job in active_jobs:
#             job.request = self.request
#             if not job.is_expired:
#                 filtered_jobs.append(job)
#         active_jobs = filtered_jobs
#         active_jobs_count = len(active_jobs)
#         candidate_applied = 0
#         candidates_hired = 0
#         candidates_in_review = 0
#         for job in active_jobs:
#             candidate_applied += job.candidate_set.count()
#             # for candidate in job.candidate_set.all():
#                 # print(candidate.name)
#             # stage = Stage.objects.get(name='Hired', job_opening=job)
#             stage = Stage.objects.filter(name='Hired', job_opening=job).first()
#             candidates_hired += CandidateStage.objects.filter(stage=stage).count()
#             stage_all = Stage.objects.filter(job_opening=job).exclude(name__in=['Hired', 'Rejected'])
#             candidates_in_review += CandidateStage.objects.filter(stage__in=stage_all).count()
#         context['active_jobs'] = active_jobs_count
#         context['candidates_applied'] = candidate_applied
#         context['candidates_hired'] = candidates_hired
#         context['candidates_in_review'] = candidates_in_review


#         context['recent_openings'] = recent_openings

#         return context


class JobOpeningView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    title = 'Job Openings'

    def dispatch(self, request, *args, **kwargs):
        # Redirect to default 'active' status if not provided
        if 'status' not in request.GET:
            return redirect(f"{request.path}?status=active")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['user'] = self.request.user

        # Access permission details (optional)
        has_perm = self.request.user.groups.filter(permissions__codename='add_jobopening').exists()
        context['has_perm'] = has_perm
        self.request.session['previous_page'] = ''

        # New: filter from ?status=active or ?status=closed
        status_filter = self.request.GET.get('status')  # 'active' or 'closed'

        if self.request.user.is_superuser:
            job_posts = JobOpening.objects.all().order_by('-active', '-updated_on')
            
            if status_filter == 'active':
                job_posts = job_posts.filter(active=True)
            elif status_filter == 'closed':
                job_posts = job_posts.filter(active=False)
            
            

            if job_posts.exists():
                for job in job_posts:
                    if job.is_expired:
                        job.active = False
                        job.save()
                context['new_application_counts'] = {job.id: job.candidate_set.filter(is_new=True).count() for job in
                                           job_posts}  # Count new applications

                context['job_posts'] = job_posts
            else:
                context['no_job_posts'] = 'No openings'
        elif self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            job_posts = JobOpening.objects.filter(company=self.request.user.employee.company).order_by('-active', '-updated_on')

            if status_filter == 'active':
                job_posts = job_posts.filter(active=True)
            elif status_filter == 'closed':
                job_posts = job_posts.filter(active=False)

            if job_posts.exists():
                for job in job_posts:
                    job.request = self.request  # Inject the request
                    if job.is_expired:
                        job.active = False
                        job.save()
                context['new_application_counts'] = {job.id: job.candidate_set.filter(is_new=True).count() for job in
                                                     job_posts}  # Count new applications
                context['job_posts'] = job_posts
            else:
                context['no_job_posts'] = 'No openings'
        else:
            employee = Employee.objects.get(user=self.request.user)

            try:
                job_posts = JobOpening.objects.filter(company=employee.company, assignemployee=employee).order_by('-active', '-updated_on')

                if status_filter == 'active':
                    job_posts = job_posts.filter(active=True)
                elif status_filter == 'closed':
                    job_posts = job_posts.filter(active=False)

                if job_posts.exists():
                    for job in job_posts:
                        job.request = self.request
                        if job.is_expired:
                            job.active = False
                            job.save()
                    context['new_application_counts'] = {job.id: job.candidate_set.filter(is_new=True).count() for job
                                                         in
                                                         job_posts}  # Count new applications
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

        # Optimize queries by prefetching related data
        stages = stages.prefetch_related(
            Prefetch(
                'candidatestage_set',
                queryset=CandidateStage.objects.select_related('candidate')
                .prefetch_related(
                    Prefetch(
                        'candidate__analysis',
                        queryset=ResumeAnalysis.objects.filter(job_opening_id=job_opening_id)
                    )
                )
                .order_by('-moved_at')  
            )
        )
        serializer = self.serializer_class(stages, many=True, context={'job_opening_id': job_opening_id})
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
            candidate_stage = CandidateStage(stage=stage, candidate=candidate, order=order+1,moved_at=timezone.now())
            candidate_stage.save()

        serializer = self.serializer_class(stage)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        order = request.data.get('order', [])
        stage_id = request.data.get('stage_id')
        send_email = request.data.get('send_email', False)  # New flag
        cc_emails = request.data.get("cc_emails", [])
        job_opening_id = self.kwargs.get('pk')
        job_opening = JobOpening.objects.get(id=job_opening_id)
        if stage_id:
            stage = Stage.objects.get(id=stage_id)
            for item in order:
                candidate_stage_id = item.get('id')
                candidate_order = item.get('order')
                assigned_recruiters = job_opening.assignemployee.all()

                CandidateStage.objects.filter(id=candidate_stage_id).update(order=candidate_order, stage=stage,moved_at=timezone.now())

                # send email to candidate
                candidate_stage = CandidateStage.objects.get(id=candidate_stage_id)
                candidate = candidate_stage.candidate
                if send_email:

                    # --- 1) FIRST: send mail to CLIENT with CC ---
                    if stage.name == "Sent to Client":
                        # pick first recruiter as sender
                        recruiter = assigned_recruiters.first()

                        send_stage_to_client_email(
                            recruiter=recruiter,
                            candidate=candidate,
                            job_opening=job_opening,
                            cc_list=cc_emails,
                            request=request,  
                        )

                    # --- 2) THEN: send mails to recruiters ---
                    for recruiter in assigned_recruiters:

                        if stage.name == "Hired":
                            send_hired_email(recruiter, candidate, job_opening)

                        elif stage.name == "Rejected":
                            send_rejected_email(recruiter, candidate, job_opening)

                        else:
                            send_stage_change_email(recruiter, candidate, job_opening, stage)

                # if stage.name == "Sent to Client":
                #     send_stage_to_client_email(request.user, candidate, job_opening)

                # elif stage.name == 'Hired':
                #     send_hired_email(request.user, candidate, job_opening)

                # elif stage.name == 'Rejected':
                #     send_rejected_email(request.user, candidate, job_opening)

                # else:
                #     send_stage_change_email(request.user, candidate, job_opening, stage)

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
        # Get candidate_id from URL parameters or from POST data
        candidate_id = self.request.GET.get('candidate_id')
        
        # Initialize candidate as None
        context['candidate'] = None
        
        if candidate_id:
            try:
                context['candidate'] = get_object_or_404(Candidate, pk=candidate_id)
            except Candidate.DoesNotExist:
                pass
        job_opening.request = self.request  # Inject the request
        
        context['s_skills'] = job_opening.requiredskills
       
        context['active'] = job_opening.active

        # Retrieve stages and candidates
        stages = Stage.objects.filter(job_opening=job_opening).order_by('order')
        context['stages'] = stages


        # Add data to the context
        context['job_opening'] = job_opening


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

        order = CandidateStage.objects.filter(stage_id=stage_id).aggregate(Max('order'))['order__max'] or 0

        # stageid = request.data.get('stage_id')
        CandidateStage.objects.filter(id=candidate_stage_id).update(order=order+1, stage_id=stage_id)
        return HttpResponseRedirect(reverse('job-process', kwargs={'pk': self.kwargs['pk']}))


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['candidates'] = Candidate.objects.filter(
        #     company=self.request.user.employee.company
        # ).only('id', 'name').order_by('-updated')
        context['designation'] = JobOpening.objects.filter(company=self.request.user.employee.company, active=True).only('id', 'designation')
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
        # Parse the JSON string into a Python list of dictionaries
        attendees_list = json.loads(interviewer)

        # Extract email addresses from the 'value' key of each dictionary
        email_list = [attendee['value'] for attendee in attendees_list]
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
            event.interviewer = email_list
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
                interviewer=email_list,
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
        event_title = event.title
        event_start = event.start_datetime.isoformat()
        event_end = event.end_datetime.isoformat()
        candidate = event.candidate
        interviewer = event.interviewer
        attendees = [candidate.email]
        attendees.extend(interviewer)
        send_interview_email(request.user, candidate, designation, event)
        for e in email_list:
            send_schedule_interview_email(request.user, e, event)
        # meeting_url = create_teams_meeting(request.user, event_title, event_start, event_end, attendees)

        # if meeting_url:
        #     # You can save the meeting URL to the event or send an email
        #     print(f"Meeting created: {meeting_url}")
        # Return a success response
        return JsonResponse({'status': 'success', 'event_data': event_data})

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)
        id = data.get('id')
        event = Event.objects.get(id=id)
        event.delete()
        return JsonResponse({'status': 'success'})

class CandidateCalendarListView(View):
    def get(self, request):
        q = request.GET.get("q", "")
        candidates = Candidate.objects.filter(
            company=request.user.employee.company,
            name__icontains=q
        ).only("id", "name")
        data = [{"id": c.id, "name": c.name} for c in candidates]
        return JsonResponse(data, safe=False)




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

# views.py
from django.db import IntegrityError
@method_decorator(csrf_exempt, name='dispatch')
class SendInterviewLinkView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            candidate_id = data.get('candidate_id')
            job_opening_id = data.get('job_opening_id')
            additional_notes = data.get('additional_notes', '')

            if not candidate_id or not job_opening_id:
                return JsonResponse({'status': 'error', 'message': 'Missing required parameters'}, status=400)

            candidate = Candidate.objects.get(id=candidate_id)

            # Check if already sent
            if InterviewInvitation.objects.filter(candidate=candidate, job_opening_id=job_opening_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Interview link already sent to this candidate for this job.'
                }, status=400)

            # Save first to prevent race condition
            InterviewInvitation.objects.create(candidate=candidate, job_opening_id=job_opening_id)

            send_interview_invitation_email(
                candidate=candidate,
                job_opening_id=job_opening_id,
                additional_notes=additional_notes
            )

            return JsonResponse({'status': 'success', 'message': 'Interview invitation sent successfully'})

        except Candidate.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Candidate not found'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

from django.http import JsonResponse
from manager.models import ClientEmail, JobOpening

def get_client_emails(request, job_opening_id):
    job = JobOpening.objects.get(id=job_opening_id)
    client = job.client

    emails = []

    # 1️⃣ Main client email
    if client is None:
        return JsonResponse({'error': 'No client assigned'})
    if client.email:
        emails.append(client.email)

    # 2️⃣ Alternative email (jo blank na hoy to)
    if client.alternative_email:
        emails.append(client.alternative_email)

    # 3️⃣ All emails from ClientEmail model
    extra_emails = list(
        ClientEmail.objects.filter(client=client)
        .values_list('email', flat=True)
    )

    emails += extra_emails

    return JsonResponse({
        "emails": emails
    })

from django.shortcuts import render, get_object_or_404
from candidate.models import Candidate, JobOpening

def candidate_analysis_pdf_view(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    job_opening = candidate.job_openings.last()

    analysis = candidate.analysis.filter(
        job_opening=job_opening
    ).first()

    return render(
        request,
        "candidate/candidate_analysis_pdf.html",
        {
            "candidate": candidate,
            "job_opening": job_opening,
            "text": analysis,
        }
    )

# def landing_page(request):
#     return render(request, "dashboard/landing.html")


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')   

    return render(request, "dashboard/landing.html")


import csv
from django.http import HttpResponse
from django.utils.timezone import localtime
from collections import defaultdict

# def download_stage_csv(request, job_opening_id):
#     job = JobOpening.objects.get(id=job_opening_id)

#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="job_{job.id}_candidates_full.csv"'

#     writer = csv.writer(response)

#     # ✅ HEADER (ALL FIELDS LIKE DETAIL PAGE)
#     writer.writerow([
#         "Name", "Email", "Contact", "Location", "DOB",
#         "Education",
#         "LinkedIn", "GitHub", "Portfolio", "Blog",
#         "Experience", "Current Designation", "Current Organization",
#         "Notice Period",
#         "Current CTC", "Current CTC (In Hand)",
#         "Expected CTC", "Expected CTC (In Hand)",
#         "Offer In Hand",
#         "Reason For Change", "Feedback",
#         "Stage", "Stage Date"
#     ])

#     # ✅ Get ALL stage records (date-wise)
#     candidate_stages = CandidateStage.objects.filter(
#         stage__job_opening=job
#     ).select_related('candidate', 'stage').order_by('candidate__id', 'moved_at')

#     for cs in candidate_stages:
#         c = cs.candidate

#         writer.writerow([
#             c.name,
#             c.email,
#             c.contact,
#             c.location,
#             c.dob.strftime('%Y-%m-%d') if c.dob else "",
#             c.education,

#             c.linkedin,
#             c.github,
#             c.portfolio,
#             c.blog,

#             c.experience,
#             c.current_designation,
#             c.current_organization,
#             c.notice_period,

#             c.current_ctc,
#             c.current_ctc_ih,
#             c.expected_ctc,
#             c.expected_ctc_ih,
#             c.offer_in_hand,

#             c.reason_for_change,
#             c.feedback,

#             cs.stage.name,
#             cs.moved_at.strftime('%Y-%m-%d %H:%M')
#         ])

#     return response

import csv
from django.http import HttpResponse
from collections import defaultdict
from manager.models import JobOpening
from .models import CandidateStage


def download_stage_csv(request, job_opening_id):
    job = JobOpening.objects.get(id=job_opening_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="job_{job.id}_candidates_full.csv"'

    writer = csv.writer(response)

    # ✅ HEADER (ALL FIELDS LIKE DETAIL PAGE)
    writer.writerow([
        "Name", "Email", "Contact", "Location", "DOB",
        "Education",
        "LinkedIn", "GitHub", "Portfolio", "Blog",
        "Experience", "Current Designation", "Current Organization",
        "Notice Period",
        "Current CTC", "Current CTC (In Hand)",
        "Expected CTC", "Expected CTC (In Hand)",
        "Offer In Hand",
        "Reason For Change", "Feedback",
        "Stage", "Stage Date"
    ])

    # ✅ GROUP DATA BY CANDIDATE
    candidate_dict = defaultdict(list)

    for cs in CandidateStage.objects.filter(
        stage__job_opening=job
    ).select_related('candidate', 'stage'):
        candidate_dict[cs.candidate].append(cs)

    # ✅ SORT CANDIDATES (LATEST ACTIVITY FIRST)
    sorted_candidates = sorted(
        candidate_dict.items(),
        key=lambda x: max(c.moved_at for c in x[1]),
        reverse=True
    )

    # ✅ WRITE DATA
    for candidate, stages in sorted_candidates:

        # sort stages inside candidate (latest first)
        stages = sorted(stages, key=lambda x: x.moved_at, reverse=True)

        for cs in stages:
            c = cs.candidate

            writer.writerow([
                c.name,
                c.email,
                c.contact,
                c.location,
                c.dob.strftime('%Y-%m-%d') if c.dob else "",
                c.education,

                c.linkedin,
                c.github,
                c.portfolio,
                c.blog,

                c.experience,
                c.current_designation,
                c.current_organization,
                c.notice_period,

                c.current_ctc,
                c.current_ctc_ih,
                c.expected_ctc,
                c.expected_ctc_ih,
                c.offer_in_hand,

                c.reason_for_change,
                c.feedback,

                cs.stage.name,
                cs.moved_at.strftime('%Y-%m-%d %H:%M')
            ])

        # ✅ optional: blank line between candidates
        writer.writerow([])

    return response