import verify_email.views
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from screening.decorators import logout_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from verify_email.email_handler import send_verification_email
from django.contrib.auth.models import Group, User
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from .models import Employee
from django.shortcuts import get_object_or_404


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


class UserDetailView(LoginRequiredMixin, CreateView):
    model = Employee
    fields = ['name', 'contact']
    template_name = 'users/enter_details.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #     return employee

    def form_valid(self, form):
        user = self.request.user
        pk = self.kwargs.get('pk')  # Get primary key from URL keyword argument
        employee = get_object_or_404(Employee, pk=pk)  # Securely retrieve employee
        # employee = form.save(commit=False)  # Don't save employee yet (for OneToOneField)
        # employee.user = user
        if user!=employee.user:
            form.add_error('name', 'You cannot change other user\'s details')
            return super().form_invalid(self)

        employee.name = form.cleaned_data['name']
        employee.contact = form.cleaned_data['contact']

        employee.save()
        return redirect('dashboard')

