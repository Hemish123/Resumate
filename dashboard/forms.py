from django import forms
from .models import Stage, CandidateStage

class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['name']