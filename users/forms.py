from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.validators import EmailValidator


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(validators=[EmailValidator])

    def clean_email(self):
        # Convert email to lowercase
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address already exists.")
        return email


    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with the specified email address!")
        return email
