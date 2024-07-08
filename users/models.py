from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import FileExtensionValidator, EmailValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group


# Create your models here.
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User model
    name = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=12, unique=True, blank=True)
    joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

