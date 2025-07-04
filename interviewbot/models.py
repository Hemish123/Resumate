from django.db import models
from manager.models import JobOpening

class InterviewAnswer(models.Model):
    job_opening = models.ForeignKey(JobOpening, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    given_answer = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True)
    video = models.FileField(upload_to='interviews/',null=True, blank=True)  # Save video to media directory
    submitted_at = models.DateTimeField(auto_now_add=True)
