from django.db import models
from django.core.validators import FileExtensionValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import Employee, Company
from candidate.models import Candidate
from manager.models import JobOpening



class Stage(models.Model):
    job_opening = models.ForeignKey(JobOpening, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class CandidateStage(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)  # To maintain order within the stage

    class Meta:
        ordering = ['order']


class Event(models.Model):
    title = models.CharField(max_length=100)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    interviewer = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=256)
    choices = [('facetoface', 'Face to face'), ('virtual', 'Virtual'), ('telephonic', 'Telephonic')]
    interview_type = models.CharField(max_length=100, choices=choices)
    interview_url = models.URLField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_datetime']
