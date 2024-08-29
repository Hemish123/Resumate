from django.contrib import admin

# Register your models here.
from .models import Client, JobOpening, Application


admin.site.register(Client)
admin.site.register(JobOpening)
admin.site.register(Application)
