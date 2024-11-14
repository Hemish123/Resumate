from django import forms
from .models import Candidate

class CandidateImportForm(forms.Form):
    file = forms.FileField()

# class UploadForms(forms.ModelForm):
#     class Meta:
#         model = Resume
#         fields = ['upload_resume']
#         widgets = {
#             'upload_resume': forms.FileInput(attrs={'id': 'fileInput', 'allow_multiple_selected': True}),
#         }

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'email', 'contact', 'location', 'linkedin', 'github',
                  'portfolio', 'blog', 'education', 'experience', 'current_designation', 'current_organization',
                  'upload_resume']
        # widgets = {
        #     'dob' : forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy'}, format='%d/%m/%Y'),
        #     'doc': forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy'}, format='%d/%m/%Y'),
        # }
        # input_formats = {
        #     'dob': ['%d/%m/%Y'],
        #     'doc': ['%d/%m/%Y'],
        # }