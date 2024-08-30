from django.db import models
from django.core.validators import FileExtensionValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import Employee, Company
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=400, blank=True)
    email = models.EmailField(validators=[EmailValidator], unique=True)
    contact = models.CharField(max_length=12, blank=True)
    website = models.URLField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)


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
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
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

    HIRING_FOR_CHOICES = [
        ('self', 'Hiring for self'),
        ('client', 'Hiring for client'),
    ]
    hiring_for = models.CharField(max_length=10, choices=HIRING_FOR_CHOICES, default='self')


    def __str__(self):
        return self.designation

    class Meta:
        ordering = ['-updated_on']
    
