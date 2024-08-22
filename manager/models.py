from django.db import models
from django.core.validators import FileExtensionValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import Employee
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=400, blank=True)
    email = models.EmailField(validators=[EmailValidator], unique=True)
    contact = models.CharField(max_length=12, blank=True)
    website = models.URLField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # Convert email to lowercase
        super().save(*args, **kwargs)

def exempt_zero(value):
    if value == 0:
        raise ValidationError(
            ('Please enter a value greater than 0'),
            params={'value': value},
        )



class JobOpening(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    designation = models.CharField(max_length=255)
    openings = models.PositiveIntegerField(validators=[exempt_zero])
    requiredskills = models.TextField(blank=True)
    jobdescription = models.FileField(blank=True, upload_to='jd/',
                                     validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'txt'],
                                                                        message='Select pdf, docx, doc or txt files only')])
    budget = models.PositiveIntegerField(default=0)
    job_type = models.CharField(max_length=50,blank=True, choices=[('Contractual', 'Contractual'),
                                                        ('Permanent', 'Permanent')])
    job_mode = models.CharField(max_length=50,blank=True, choices=[('Office', 'Office'),
                                                        ('Remote', 'Remote'),
                                                        ('Hybrid', 'Hybrid')])
    updated_on = models.DateTimeField(default=timezone.now)
    jd_content = models.TextField(blank=True)
    assignemployee = models.ManyToManyField(Employee)
    # assignemployee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # ForeignKey to Employee
    content_type = models.CharField(blank=True, max_length=10, choices=[('file', 'File'), ('text', 'Text')])  # Choice for content type
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.designation

    class Meta:
        ordering = ['-updated_on']
    
class Application(models.Model):
    job_opening = models.ForeignKey(JobOpening, on_delete=models.CASCADE)
    file_upload = models.FileField(upload_to='applications/', blank=True)
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Application for {self.job_opening.designation} on {self.updated_on}"