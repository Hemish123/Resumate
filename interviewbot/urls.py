from django.urls import path
from .views import InterviewPageView, GetQuestionView, SubmitAnswerView,ResetInterviewView

urlpatterns = [
    path('', InterviewPageView.as_view(), name='interview'),
    path('get-question/', GetQuestionView.as_view(), name='get_question'),
    path('submit-answer/', SubmitAnswerView.as_view(), name='submit_answer'),
    path('reset/', ResetInterviewView.as_view(), name='reset_interview'),
]
