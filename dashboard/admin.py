from django.contrib import admin
from .models import Stage, CandidateStage, Event

# Register your models here.
admin.site.register(Stage)
admin.site.register(CandidateStage)
admin.site.register(Event)