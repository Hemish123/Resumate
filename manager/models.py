from datetime import timedelta
from django.db import models
from django.core.validators import FileExtensionValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from twisted.python.usage import UsageError
from django.contrib.auth.models import User
from users.models import Employee, Company



# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=400, blank=True)
    email = models.EmailField(validators=[EmailValidator], unique=True)
    contact = models.CharField(max_length=12, blank=True)
    website = models.URLField(max_length=100, blank=True)
    company = models.CharField(max_length=255)
    joined = models.DateTimeField(default=timezone.now)  #(Agreement date)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='client_created')
    linkedin = models.URLField(max_length=200, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    gst_no = models.CharField(max_length=50, blank=True)
    # payment_id = models.CharField(max_length=100, blank=True)
    alternative_email = models.EmailField(blank=True,null=True)
    alternative_contact = models.CharField(max_length=12, blank=True)
    agreement_upload = models.FileField(upload_to='agreements/', blank=True, null=True)
    # document_upload = models.FileField(upload_to='documents/', blank=True, null=True)
    client_id = models.CharField(max_length=20, unique=True,null=True)
    street = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    client_location = models.CharField(max_length=400, blank=True)
    payment_period = models.PositiveIntegerField(blank=True, null=True)
    replacement_period = models.PositiveIntegerField(blank=True, null=True)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    commercials_decided = models.TextField(blank=True, null=True)

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
class ClientDocument(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
class ClientEmail(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='additional_emails')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.email} ({self.client.name})"

class HiringPOC(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='hiring_pocs'
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    designation = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    contact = models.CharField(max_length=15, blank=True)
    linkedin = models.URLField(blank=True)

    def __str__(self):
        return f"{self.client.name} - {self.name} (Hiring)"

class PaymentPOC(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='payment_pocs'
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    designation = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    contact = models.CharField(max_length=15, blank=True)
    linkedin = models.URLField(blank=True)

    def __str__(self):
        return f"{self.client.name} - {self.name} (Payment)"



class JobOpening(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    designation = models.CharField(max_length=255)
    openings = models.PositiveIntegerField(validators=[exempt_zero])
    requiredskills = models.TextField(blank=True)
    min_experience = models.PositiveIntegerField(default=0)
    max_experience = models.PositiveIntegerField(default=1)
    education = models.CharField(max_length=255, default="graduate", blank=True)
    jobdescription = models.FileField(blank=True, upload_to='jd/',
                                     validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'txt'],
                                                                        message='Select pdf, docx, doc or txt files only')])
    budget = models.FloatField(default=0)
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
    expires = models.IntegerField(default=21)
    skills_criteria = models.IntegerField(default=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default="1", related_name='jobopening')
    location = models.CharField(max_length=255, null=True, blank=True)
    HIRING_FOR_CHOICES = [
        ('self', 'Hiring for self'),
        ('client', 'Hiring for client'),
    ]
    hiring_for = models.CharField(max_length=10, choices=HIRING_FOR_CHOICES, default='self')
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    @property
    def active_till(self):
        return self.created_at + timedelta(days=self.expires)


    def __str__(self):
        return self.designation

    @property
    def expiration_date(self):
        """Calculate the expiration date based on created_date and expires."""
        return self.updated_on + timezone.timedelta(days=self.expires)

    @property
    def days_remaining(self):
        """Calculate the number of days remaining until expiration."""
        remaining = ((self.expiration_date - timezone.now()).days) + 1
        return max(remaining, 0)  # Return 0 if already expired

    @property
    def is_expired(self):
        """Check if the job opening is expired."""
        if hasattr(self, 'request') and self.request.user.is_authenticated and self.request.user.employee.company.name == "JMS Advisory":
            return False

        return timezone.now() > self.expiration_date

    class Meta:
        ordering = ['-updated_on']
    
