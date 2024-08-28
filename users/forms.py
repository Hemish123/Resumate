from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.validators import EmailValidator


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(validators=[EmailValidator])
    full_name = forms.CharField(max_length=255)

    def clean_email(self):
        # Convert email to lowercase
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.username = user.email  # Use email as username
        full_name = self.cleaned_data['full_name']
        first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
        user.first_name = first_name
        user.last_name = last_name
        if commit:
            user.save()

        return user

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password1', 'password2']



class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with the specified email address!")
        return email
