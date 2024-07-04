from django.db import models
from django.core.validators import FileExtensionValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=400, blank=True)
    email = models.EmailField(validators=[EmailValidator], unique=True)
    contact = PhoneNumberField(blank=True)
    website = models.URLField(max_length=100, blank=True)


    def __str__(self):
        return self.name


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
    requiredskills = models.CharField(max_length=1000, blank=True)
    jobdescription = models.FileField(blank=True, upload_to='jd/',
                                     validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'txt'],
                                                                        message='Select pdf, docx, doc or txt files only')])
    updated_on = models.DateTimeField(default=timezone.now)
    jd_content = models.TextField(blank=True)
    assignemployee = models.CharField(max_length=255)
    # assignemployee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # ForeignKey to Employee
    content_type = models.CharField(blank=True, max_length=10, choices=[('file', 'File'), ('text', 'Text')])  # Choice for content type
