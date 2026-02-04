from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.validators import EmailValidator
import re

BANNED_EMAIL_PREFIXES = ['dummy', 'test', 'abc', 'user', 'example']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(validators=[EmailValidator])
    full_name = forms.CharField(max_length=255)


    def clean_email(self):
        # Convert email to lowercase
        email = self.cleaned_data['email'].lower()

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address already exists.")

        # Check for banned/dummy emails
        local_part = email.split('@')[0]  # part before @
        if local_part in BANNED_EMAIL_PREFIXES:
            raise forms.ValidationError("Please use a valid email address, not a dummy one.")

        # # Optional: restrict to certain domains (e.g., gmail, yahoo, outlook)
        # allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com']
        # domain = email.split('@')[1]
        # if domain not in allowed_domains:
        #     raise forms.ValidationError(f"Registration allowed only with {', '.join(allowed_domains)} accounts.")

        return email

    
    # def clean_email(self):
    #     # Convert email to lowercase
    #     email = self.cleaned_data['email'].lower()
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError("This email address already exists.")
    #     return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        errors = []

        # Password validation rules
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>).")

        if errors:
            # Join all error messages and raise ValidationError
            raise forms.ValidationError(errors)

        return password
    
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

class SupportForm(forms.Form):
    email = forms.EmailField(validators=[EmailValidator])
    subject = forms.CharField(max_length=500)
    message = forms.CharField(widget=forms.Textarea)


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with the specified email address!")
        return email
