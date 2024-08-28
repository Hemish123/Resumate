from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password
from .utils import generate_random_password, send_activation_email
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from users.models import Employee
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin



class CreateEmployeeView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    fields = ['email', 'groups']  # Or use form fields if using forms.ModelForm
    template_name = 'adminuser/create_employee.html'
    permission_required = 'users.add_employee'  # Replace with actual permission codename


    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_employee').exists()

    def form_valid(self, form):
        user = get_user_model()()  # Create user instance
        user.email = form.cleaned_data['email'].lower()
        user.username = user.email

        if User.objects.filter(email=user.email).exists():
            form.add_error('email', 'email already exists')

        if form.errors:
            return super().form_invalid(form)
        password = generate_random_password()
        user.password = make_password(password)
        user.save()
        selected_group_id = self.request.POST.get('groups')
        # Add the user to the selected group (if any)

        group = Group.objects.get(pk=selected_group_id)
        # group = form.cleaned_data['group']  # Replace 'admin' with your actual group name
        print(group)
        user.groups.add(group)

        employee = Employee.objects.create(user=user)  # Don't save employee yet (for OneToOneField)
        employee.save()

        site_url = self.request.META.get('HTTP_HOST')  # Get current domain for activation link
        send_activation_email(employee, site_url, password)

        return redirect('dashboard')  # Redirect to success page (optional)
