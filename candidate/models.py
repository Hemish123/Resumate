from django.db import models

# Create your models here.

from django.core.validators import FileExtensionValidator, EmailValidator
from django.contrib.auth.models import User
from manager.models import JobOpening
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

# Create your models here.

def today():
    return timezone.now().date()

class Candidate(models.Model):
    job_openings = models.ManyToManyField(JobOpening, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(validators=[EmailValidator], unique=True)
    contact = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    dob = models.DateField(blank=True, null=True)
    doc = models.DateField(default=today, blank=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)
    github = models.URLField(max_length=255, blank=True, null=True)
    portfolio = models.URLField(max_length=255, blank=True, null=True)
    blog = models.URLField(max_length=255, blank=True, null=True)
    education = models.CharField(max_length=255)
    experience = models.PositiveIntegerField(blank=True, default=0)
    current_designation = models.CharField(max_length=255, blank=True, null=True)
    current_organization = models.CharField(max_length=255, blank=True, null=True)
    current_ctc = models.FloatField(max_length=255, blank=True, default=0)
    current_ctc_ih = models.FloatField(max_length=255, blank=True, default=0)
    expected_ctc = models.FloatField(max_length=255, blank=True, default=0)
    expected_ctc_ih = models.FloatField(max_length=255, blank=True, default=0)
    offer_in_hand = models.FloatField(max_length=255, blank=True, default=0)
    notice_period = models.PositiveIntegerField(blank=True, default=0)
    reason_for_change = models.CharField(max_length=500, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # Convert email to lowercase
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.linkedin:
            if not self.linkedin.startswith(('http://', 'https://')):
                self.linkedin = 'http://' + self.linkedin

        if self.github:
            if not self.github.startswith(('http://', 'https://')):
                self.github = 'http://' + self.github

        if self.portfolio:
            if not self.portfolio.startswith(('http://', 'https://')):
                self.portfolio = 'http://' + self.portfolio

        if self.blog:
            if not self.blog.startswith(('http://', 'https://')):
                self.blog = 'http://' + self.blog



class Resume(models.Model) :
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='resume')
    upload_resume = models.FileField(upload_to='resumes/',
                                     validators=[FileExtensionValidator(allowed_extensions=['pdf','docx','doc'],
                                                                        message='Select pdf, docx or doc files only')])
    updated_on = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    filename = models.CharField(max_length=255 , blank=True)
    text_content = models.TextField()


    def __str__(self):
        return self.filename

    def get_absolute_url(self):
        return reverse('parsing-home')

    def save(self, *args, **kwargs):
        if self.upload_resume:
            # Extract the original filename
            self.filename = self.upload_resume.name
        super().save(*args, **kwargs)

