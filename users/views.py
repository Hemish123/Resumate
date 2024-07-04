import verify_email.views
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from screening.decorators import logout_required
from django.core.mail import send_mail
from verify_email.email_handler import send_verification_email
from django.contrib.auth.models import Group



@logout_required
def register(request):
    if request.method == 'POST' :
        user_create = UserRegisterForm(request.POST)
        if user_create.is_valid():
            messages.success(request, f'Check your email and verify using link sent in your email')
            # send link to mail and save user if link verified
            inactive_user = send_verification_email(request, user_create)
            admin_group = Group.objects.get(name='admin')  # Replace 'admin' with your actual group name
            inactive_user.groups.add(admin_group)

    else:
        user_create = UserRegisterForm()
    return render(request, 'users/register.html', {'form' : user_create})
