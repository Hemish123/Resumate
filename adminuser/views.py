
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from .utils import generate_random_password, send_activation_email
from django.views.generic import ListView, CreateView, TemplateView, DeleteView, UpdateView
from users.models import Employee
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib import messages


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
        # selected_group_id = self.request.POST.get('groups')
        # # Add the user to the selected group (if any)

        # group = Group.objects.get(pk=selected_group_id)
        # # group = form.cleaned_data['group']  # Replace 'admin' with your actual group name

        # user.groups.add(group)
        group = form.cleaned_data['groups']
        if group:
            user.groups.set(group)


        company = self.request.user.employee.company

        employee = Employee.objects.create(user=user, company=company,name=self.request.POST.get('name'),
        contact=self.request.POST.get('contact'),
        designation=self.request.POST.get('designation')) 
        employee.save()

        site_url = self.request.META.get('HTTP_HOST')  # Get current domain for activation link
        send_activation_email(employee, site_url, password)
        messages.success(self.request, message='Success! Email sent to employee with login details.')

        return redirect('users-settings')  # Redirect to success page (optional)

class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'groups']
    template_name = "adminuser/update_employee.html"
    title = "Update Client"
    permission_required = 'users.change_employee'   # Replace with actual permission codename
    success_url = reverse_lazy('users-settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()
        context['employee'] = context['user'].employee
        return context

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='change_employee').exists()

    def form_valid(self, form):

        user = self.object                      # User object
        employee = user.employee               # Related Employee object

        # ---- User name update ----
        user.first_name = self.request.POST.get('first_name')
        user.last_name = self.request.POST.get('last_name')
        user.save()

        # ---- MAIN FIX: Employee name update karvo PADE ----
        full_name = f"{user.first_name} {user.last_name}".strip()
        employee.name = full_name.title()      # 🔥 je list ma show thase

        employee.contact = self.request.POST.get('contact')
        employee.designation = self.request.POST.get('designation')
        employee.save()

        messages.success(self.request, "Employee updated successfully!")
        return super().form_valid(form)
