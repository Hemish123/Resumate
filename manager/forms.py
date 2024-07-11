from django import forms
from .models import Organization, JobOpening
from phonenumber_field.widgets import PhoneNumberPrefixWidget
import json


# class OrganizationForm(forms.ModelForm):
    #
    # def clean_email(self):
    #     # Convert email to lowercase
    #     email = self.cleaned_data['email'].lower()
    #     return email
    #
    # class Meta:
    #     model = Organization
    #     fields = ['name', 'location', 'email', 'contact', 'website']
    #     # widgets = {
    #     #     'contact': PhoneNumberPrefixWidget(),
    #     # }



class JobOpeningForm(forms.ModelForm):

    class Meta:
        model = JobOpening
        fields = ['organization', 'designation', 'openings', 'requiredskills', 'assignemployee', 'content_type', 'jobdescription', 'jd_content']
        widgets = {
            'organization': forms.Select(),
            'designation': forms.Select(choices=()),
            'assignemployee': forms.Select(),
            'requiredskills': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate company choices and designation choices
        self.fields['organization'].choices = [(company.pk, company.name) for company in Organization.objects.all()]


