import requests
import html
import json
from django.views import View
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponse
from .models import InterviewAnswer
from candidate.genai_resume import generate_interview_questions
from manager.models import JobOpening
from .utils import transcribe_audio_file
import tempfile
import os

class InterviewPageView(View):
    def get(self, request):
        job_opening_id = request.GET.get('job_opening')
        if not job_opening_id:
            return HttpResponseBadRequest("Missing job opening ID.")

        job_opening = get_object_or_404(JobOpening, id=job_opening_id)

        # Always recreate questions every time you load
        questions_list = generate_interview_questions(
            text=job_opening.jd_content,
            designation=job_opening.designation,
            skills_string=job_opening.requiredskills,
            min_experience=job_opening.min_experience,
            max_experience=job_opening.max_experience,
            education=job_opening.education
        )

        formatted_questions = [{"question": "Tell me about yourself.", "correct": None}]
        for q in questions_list[:4]:
            formatted_questions.append({"question": q, "correct": None})

        request.session['questions'] = formatted_questions
        request.session['current_index'] = 0
        request.session['answers'] = []

        return render(request, "interviewbot/interview.html")




class GetQuestionView(View):
    def get(self, request):
        questions = request.session.get('questions', [])
        index = request.session.get('current_index', 0)

        if index < len(questions):
            q = questions[index]
            return JsonResponse({'question': q['question']})
        return JsonResponse({'done': True})


class SubmitAnswerView(View):
    def post(self, request):
        try:
            answer = request.POST.get('answer', '').strip()
            video_file = request.FILES.get('video')
            index = request.session.get('current_index', 0)
            questions = request.session.get('questions', [])
            
            if index >= len(questions):
                return JsonResponse({'done': True})

            current_question = questions[index]

            # Save the answer to database
            InterviewAnswer.objects.create(
                question=current_question['question'],
                given_answer=answer,
                is_correct=False,
                video=video_file
            )

            # Update session
            answers = request.session.get('answers', [])
            answers.append({
                'question': current_question['question'],
                'given_answer': answer,
            })
            request.session['answers'] = answers
            request.session['current_index'] = index + 1

            return JsonResponse({'done': index + 1 >= len(questions)})
        except Exception as e:
            print("SubmitAnswerView ERROR:", e, type(e))
            return HttpResponseBadRequest(str(e))



class ResetInterviewView(View):
    def post(self, request):
        try:
            # Clear the session to reset the interview
            request.session.flush()
            return HttpResponse("Session reset successful.")
        except Exception as e:
            return HttpResponseBadRequest("Error: " + str(e))
