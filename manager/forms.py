from django import forms
from .models import Client, JobOpening,Application
from phonenumber_field.widgets import PhoneNumberPrefixWidget
import json


# class ClientForm(forms.ModelForm):
    #
    # def clean_email(self):
    #     # Convert email to lowercase
    #     email = self.cleaned_data['email'].lower()
    #     return email
    #
    # class Meta:
    #     model = Client
    #     fields = ['name', 'location', 'email', 'contact', 'website']
    #     # widgets = {
    #     #     'contact': PhoneNumberPrefixWidget(),
    #     # }



class JobOpeningForm(forms.ModelForm):

    class Meta:
        model = JobOpening
        fields = ['client', 'designation', 'openings', 'requiredskills', 'assignemployee', 'content_type', 'jobdescription', 'jd_content']
        widgets = {
            'client': forms.Select(),
            'designation': forms.Select(choices=()),
            'assignemployee': forms.Select(),
            'requiredskills': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate company choices and designation choices
        self.fields['client'].choices = [(company.pk, company.name) for company in Client.objects.all()]


