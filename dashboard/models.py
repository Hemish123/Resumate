from django.db import models
from django.core.validators import FileExtensionValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import Employee
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
