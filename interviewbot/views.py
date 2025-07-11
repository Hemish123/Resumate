import requests
import html
import json
from django.views import View
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponse
from .models import InterviewAnswer
from candidate.genai_resume import generate_next_question,transcribe_audio,evaluate_answer,generate_interview_summary

from manager.models import JobOpening
from candidate.models import Candidate,ResumeAnalysis
# from .utils import transcribe_audio_file
import tempfile
import os

# class InterviewPageView(View):
#     def get(self, request):
#         job_opening_id = request.GET.get('job_opening')
#         if not job_opening_id:
#             return HttpResponseBadRequest("Missing job opening ID.")

#         job_opening = get_object_or_404(JobOpening, id=job_opening_id)

#         # Always recreate questions every time you load
#         questions_list = generate_interview_questions(
#             text=job_opening.jd_content,
#             designation=job_opening.designation,
#             skills_string=job_opening.requiredskills,
#             min_experience=job_opening.min_experience,
#             max_experience=job_opening.max_experience,
#             education=job_opening.education
#         )

#         formatted_questions = [{"question": "Tell me about yourself.", "correct": None}]
#         for q in questions_list[:4]:
#             formatted_questions.append({"question": q, "correct": None})

#         request.session['questions'] = formatted_questions
#         request.session['current_index'] = 0
#         request.session['answers'] = []

#         return render(request, "interviewbot/interview.html")

class InterviewPageView(View):
    def get(self, request):
        job_opening_id = request.GET.get("job_opening")
        candidate_id = request.GET.get("candidate")

        if not job_opening_id or not candidate_id:
            return HttpResponseBadRequest("Missing job opening or candidate ID.")

        job_opening = get_object_or_404(JobOpening, id=job_opening_id)
        candidate = get_object_or_404(Candidate, id=candidate_id)

        # Try to get resume analysis if you want
        resume_analysis = ResumeAnalysis.objects.filter(candidate=candidate, job_opening=job_opening).first()

        request.session["answers"] = []
        request.session["current_question"] = None
        request.session["job_opening_id"] = job_opening.id
        request.session["candidate_id"] = candidate.id
        request.session["resume_analysis_id"] = resume_analysis.id if resume_analysis else None

        return render(request, "interviewbot/interview.html")




# class GetQuestionView(View):
#     def get(self, request):
#         questions = request.session.get('questions', [])
#         index = request.session.get('current_index', 0)

#         if index < len(questions):
#             q = questions[index]
#             return JsonResponse({'question': q['question']})
#         return JsonResponse({'done': True})
class GetQuestionView(View):
    def get(self, request):
        try:
            # Check if session has required data
            if not all(key in request.session for key in ['job_opening_id', 'candidate_id']):
                return JsonResponse({"error": "Session data missing"}, status=400)

            job_opening = get_object_or_404(JobOpening, id=request.session['job_opening_id'])
            candidate = get_object_or_404(Candidate, id=request.session['candidate_id'])
            resume_analysis_id = request.session.get('resume_analysis_id')
            resume_analysis = get_object_or_404(ResumeAnalysis, id=resume_analysis_id) if resume_analysis_id else None

            previous_answers = request.session.get("answers", [])

            # Stop after 15 questions
            if len(previous_answers) >= 12:
                return JsonResponse({"done": True})

            if not previous_answers:
                # First question is always fixed
                question = "Tell me about yourself."
            else:
                # Generate dynamically
                question = generate_next_question(job_opening, candidate, resume_analysis, previous_answers)

            # Store current question in session
            request.session["current_question"] = question
            request.session.modified = True

            return JsonResponse({
                "question": question,
                "done": False
            })

        except Exception as e:
            print(f"Error in GetQuestionView: {str(e)}")
            return JsonResponse({
                "error": str(e),
                "done": True
            }, status=400)

class SubmitAnswerView(View):
    def post(self, request):
        try:
            if not all(key in request.session for key in ['job_opening_id', 'candidate_id', 'current_question']):
                return JsonResponse({
                    'error': 'Session data missing',
                    'success': False
                }, status=400)

            answer = request.POST.get("answer", "").strip()
            video_file = request.FILES.get("video")
            audio_file = request.FILES.get("audio")
            question = request.session.get("current_question")

            if not question:
                return JsonResponse({
                    'error': 'No current question in session',
                    'success': False
                }, status=400)

            job_opening = get_object_or_404(JobOpening, id=request.session['job_opening_id'])
            candidate = get_object_or_404(Candidate, id=request.session['candidate_id'])
            resume_analysis_id = request.session.get('resume_analysis_id')
            resume_analysis = get_object_or_404(ResumeAnalysis, id=resume_analysis_id) if resume_analysis_id else None

            audio_transcript = None
            if audio_file:
                # Save audio to a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_audio:
                    for chunk in audio_file.chunks():
                        tmp_audio.write(chunk)
                    tmp_audio_path = tmp_audio.name

                # Use your transcribe_audio function
                audio_transcript = transcribe_audio(tmp_audio_path)

                if audio_transcript:
                    audio_transcript = audio_transcript.strip()

                # Prefer audio transcript if longer
                if audio_transcript and len(audio_transcript) > len(answer):
                    answer = audio_transcript

                # Remove temp file
                os.unlink(tmp_audio_path)

            # Create InterviewAnswer entry
            ia = InterviewAnswer.objects.create(
                job_opening=job_opening,
                candidate=candidate,
                resume_analysis=resume_analysis,
                question=question,
                given_answer=answer,
                audio_transcript=audio_transcript,
                is_correct=False,
                video=video_file
            )

            # Evaluate answer using GPT service
            eval_data = evaluate_answer(question, answer, job_opening.requiredskills)
            ia.question_score = eval_data.get("question_score")
            ia.skill_scores = eval_data.get("skill_scores")
            ia.technical_skills_score = eval_data.get("technical_skills_score")
            ia.save()

            # Update session for front-end use
            answers = request.session.get("answers", [])
            answers.append({
                "question": question,
                "answer": answer,
                "question_score": ia.question_score,
                "skill_scores": ia.skill_scores,
                "technical_skills_score": ia.technical_skills_score,
                "audio_transcript": audio_transcript,
                "video_file": video_file.name if video_file else None
            })
            request.session["answers"] = answers
            request.session["current_question"] = None
            request.session.modified = True

            return JsonResponse({
                "done": len(answers) >= 15,
                "success": True,
                "message": "Answer submitted and evaluated"
            })
        except Exception as e:
            print("Error in SubmitAnswerView:", e)
            return JsonResponse({"error": str(e), "success": False}, status=400)



class ResetInterviewView(View):
    def post(self, request):
        try:
            # Clear the session to reset the interview
            request.session.flush()
            return HttpResponse("Session reset successful.")
        except Exception as e:
            return HttpResponseBadRequest("Error: " + str(e))


class InterviewReportPageView(View):
    def get(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        answers = InterviewAnswer.objects.filter(candidate=candidate)

        if not answers.exists():
            return render(request, "interviewbot/report.html", {
                "error": "No answers found for this candidate.",
                "candidate": candidate,
            })

        skill_totals = {}
        skill_counts = {}
        total_question_score = 0
        total_technical_score = 0
        question_data = []

        for ans in answers:
            q_score = float(ans.question_score or 0)
            t_score = float(ans.technical_skills_score or 0)
            total_question_score += q_score
            total_technical_score += t_score

            question_data.append({
                "question": ans.question,
                "answer": ans.given_answer,
                "score": q_score,
                "technical_skills_score": t_score,
                "skills": ans.skill_scores or {}
            })

            if ans.skill_scores:
                for sk, sc in ans.skill_scores.items():
                    skill_totals[sk] = skill_totals.get(sk, 0) + sc
                    skill_counts[sk] = skill_counts.get(sk, 0) + 1

        skill_averages = {
            sk: round(skill_totals[sk] / skill_counts[sk], 2)
            for sk in skill_totals
        }

        # Convert to lists for the chart
        skill_labels = list(skill_averages.keys())
        skill_values = list(skill_averages.values())

        if not skill_labels:
            skill_labels = ["No Data"]
            skill_values = [0]

        avg_question_score = round(total_question_score / len(question_data), 2)
        avg_technical_score = round(total_technical_score / len(question_data), 2)

        # Generate the summary
        summary_text = generate_interview_summary(
            candidate_name=candidate.name,
            questions=question_data,
            required_skills=skill_labels
        )

        return render(request, "interviewbot/report.html", {
            "candidate": candidate,
            "questions": question_data,
            "skill_labels": skill_labels,
            "skill_values": skill_values,
            "average_question_score": avg_question_score,
            "average_technical_score": avg_technical_score,
            "summary_text": summary_text,
        })