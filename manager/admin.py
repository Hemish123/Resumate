from django.contrib import admin

# Register your models here.
from .models import Organization, JobOpening


admin.site.register(Organization)
admin.site.register(JobOpening)
