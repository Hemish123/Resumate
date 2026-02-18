from django import forms
from .models import Client, JobOpening,ClientDocument
from phonenumber_field.widgets import PhoneNumberPrefixWidget
import json
from users.models import Company
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,12}$',
    message="Enter a valid phone number (10-12 digits)."
)

class ClientOnboardingForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['client_id', 'created_by']
        fields = [
            'company','name', 'email', 'alternative_email', 'contact','alternative_contact', 'website','linkedin', 'location','street','city',
            'state','country','postal_code','client_location', 'industry', 'gst_no','status',
             'agreement_upload','commercials_decided',]
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Company Name','required':'required'}),
            'client_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client ID'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client Name','required':'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email','required':'required'}),
            'alternative_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Alternative Email'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone','required':'required'}),
            'alternative_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternative Contact'}),
            'website': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Website'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn URL'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'client_location': forms.TextInput(attrs={'class': 'form-control'}),
            # 'joined': forms.DateInput(attrs={'type': 'date','class': 'form-control' ,'placeholder': 'Agreement_Date'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Industry'}),
            'gst_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GST Number'}),
            # 'payment_period': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'replacement_period': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'commercials_decided': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Enter commercial details ','rows': 1 }),
            # 'payment_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Payment ID'}),
            'agreement_upload': forms.FileInput(attrs={'class': 'form-control'}),
            # 'document_upload': forms.FileInput(attrs={'class': 'form-control'}),
        }


    def clean_website(self):
            website = self.cleaned_data.get('website')

            if website:
                if not website.startswith(('http://', 'https://')):
                    website = 'https://' + website

            return website
    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email.lower()

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if contact:
            phone_validator(contact)
        return contact
    
    def clean_alternative_email(self):
            email = self.cleaned_data.get('alternative_email')
            if email:
                return email.lower()
            return email
    
    def clean_payment_period(self):
        value = self.cleaned_data.get('payment_period')
        if value == 0:
            raise forms.ValidationError("Payment period must be greater than 0")
        return value

    def clean_replacement_period(self):
        value = self.cleaned_data.get('replacement_period')
        if value == 0:
            raise forms.ValidationError("Replacement period must be greater than 0")
        return value

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
        fields = ['client', 'designation', 'location'  , 'openings', 'requiredskills', 'assignemployee', 'content_type', 'jobdescription', 'jd_content']
        widgets = {
            'client': forms.Select(),
            'designation': forms.Select(choices=()),
            'assignemployee': forms.Select(),
            'requiredskills': forms.Select(),
            'location':forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate company choices and designation choices
        self.fields['client'].choices = [(company.pk, company.name) for company in Client.objects.all()]


