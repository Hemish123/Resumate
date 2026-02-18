from django import forms
from .models import Candidate

class CandidateImportForm(forms.Form):
    upload_file = forms.FileField()

# class UploadForms(forms.ModelForm):
#     class Meta:
#         model = Resume
#         fields = ['upload_resume']
#         widgets = {
#             'upload_resume': forms.FileInput(attrs={'id': 'fileInput', 'allow_multiple_selected': True}),
#         }

# class CandidateForm(forms.ModelForm):
#     class Meta:
#         model = Candidate
#         fields = ['name', 'email', 'contact', 'location', 'linkedin', 'github',
#                   'portfolio', 'blog', 'education', 'experience', 'current_designation', 'current_organization',
#                   'upload_resume']
#         # widgets = {
#         #     'dob' : forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy'}, format='%d/%m/%Y'),
#         #     'doc': forms.DateInput(attrs={'placeholder': 'dd/mm/yyyy'}, format='%d/%m/%Y'),
#         # }
#         # input_formats = {
#         #     'dob': ['%d/%m/%Y'],
#         #     'doc': ['%d/%m/%Y'],
#         # }
class CandidateForm(forms.ModelForm):

        class Meta:
            model = Candidate
            fields = [
            'name',
            'email',
            'contact',
            'dob',
            'college',
            'location',
            'preferred_location',
            'education',
            'experience',
            'current_designation',
            'current_organization',
            'current_ctc',
            'expected_ctc',
            'notice_period',
            'linkedin',
            'github',
            'portfolio',
            'blog',
            'share_date',
            'upload_resume',
            ]

            widgets = {
            'share_date': forms.DateInput(attrs={'type': 'date'}),
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # ✅ Make mandatory at FORM level
            mandatory_fields = [
            'name',
            'email',
            'contact',
            'dob',
            'college',
            'location',
            'preferred_location',
            'education',
            'experience',
            'current_designation',
            'current_organization',
            'current_ctc',
            'expected_ctc',
            'notice_period',
            'share_date',
            ]

            for field in mandatory_fields:
                self.fields[field].required = True

        def clean(self):
                cleaned_data = super().clean()
                current = cleaned_data.get('current_ctc')
                expected = cleaned_data.get('expected_ctc')

                if current is not None and expected is not None:
                    if expected < current:
                        self.add_error(
                        'expected_ctc',
                        'Expected CTC cannot be less than Current CTC'
                        )
        