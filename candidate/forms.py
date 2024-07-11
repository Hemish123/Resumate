from django import forms
from .models import Resume, Candidate


class UploadForms(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['upload_resume']
        widgets = {
            'upload_resume': forms.FileInput(attrs={'id': 'fileInput', 'allow_multiple_selected': True}),
        }

# class CandidateForm(forms.ModelForm):
#     class Meta:
#         model = Candidate
#         fields = ['job_openings', 'name', 'email', 'contact', 'location', 'dob', 'doc', 'website', 'education',
#                   'experience', 'current_designation', 'current_organization', 'current_ctc', 'expected_ctc',
#                   'offer_in_hand', 'notice_period', 'reason_for_change', 'feedback']
#         widgets = {
#             'dob' : forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy'}, format='%d/%m/%Y'),
#             'doc': forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy'}, format='%d/%m/%Y'),
#         }
#         input_formats = {
#             'dob': ['%d/%m/%Y'],
#             'doc': ['%d/%m/%Y'],
#         }