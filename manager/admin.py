from django.contrib import admin

# Register your models here.
from .models import Organization, JobOpening, Application


admin.site.register(Organization)
admin.site.register(JobOpening)
admin.site.register(Application)
