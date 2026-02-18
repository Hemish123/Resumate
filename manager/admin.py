from django.contrib import admin

# Register your models here.
from .models import Client, JobOpening,ClientEmail,ClientDocument


admin.site.register(Client)
admin.site.register(JobOpening)
admin.site.register(ClientEmail)
admin.site.register(ClientDocument)

