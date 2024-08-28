import verify_email.views
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from screening.decorators import logout_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from verify_email.email_handler import send_verification_email
from django.contrib.auth.models import Group, User
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from .models import Employee, Company
from manager.models import Organization
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


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

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user

        # Check if the user has completed setup
        if user.groups.filter(name='admin').exists() and (not user.company.exists()):  # Assuming you have a Profile model with this field
            return reverse_lazy('company-create')  # Redirect to 'create_company' URL

        # Default success URL if setup is completed
        return super().get_success_url()

class CompanyCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Company
    fields = ['name', 'website', 'description']
    template_name = 'users/create_company.html'
    permission_required = 'users.add_company'  # Replace with actual permission codename

    def has_permission(self):
        # Override has_permission to consider inherited group permissions
        user = self.request.user
        return user.groups.filter(permissions__codename='add_company').exists()

    def form_valid(self, form):
        user = self.request.user
        pk = self.kwargs.get('pk')  # Get primary key from URL keyword argument
        company = form.save(commit=False)
        company.created_by = user
        company.save()
        employee = Employee.objects.create(user=user, company=company)  # Securely retrieve employee
        employee.save()
        # employee = form.save(commit=False)  # Don't save employee yet (for OneToOneField)
        # employee.user = user
        # if user!=employee.user:
        #     form.add_error('name', 'You cannot change other user\'s details')
        #     return super().form_invalid(self)

        return redirect('dashboard')

class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Employee
    fields = ['contact']
    template_name = 'users/enter_details.html'

    def test_func(self):
        # Ensure that only the user with the correct ID can access the page
        employee = get_object_or_404(Employee, pk=self.kwargs['pk'])
        return self.request.user == employee.user

    def handle_no_permission(self):
        # Provide a forbidden response if the user is not authorized
        if not self.request.user.is_authenticated:
            # Redirect to login page if not authenticated
            return super().handle_no_permission()
        return HttpResponseForbidden("You do not have permission to access this page.")

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

        full_name = self.request.POST.get('full_name')
        if full_name:
            first_name, last_name = (full_name.split(' ', 1) + [''])[:2]
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        employee.contact = form.cleaned_data['contact']

        employee.save()
        return redirect('dashboard')

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "users/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['organizations'] = Organization.objects.all()[:5]
      # Add employee data


        has_perm2 = self.request.user.groups.filter(permissions__codename='view_employee').exists()
        context['employees'] = Employee.objects.all()[:5]
        context['has_perm2'] = has_perm2
        

        return context
    
    

class OrganizationsListView(LoginRequiredMixin, TemplateView):
    template_name = "users/organizations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['organizations'] = Organization.objects.all()

         # Access permission details (optional)
        has_perm1 = self.request.user.groups.filter(permissions__codename='add_organization').exists()
        context['has_perm1'] = has_perm1
        
        has_perm2 = self.request.user.groups.filter(permissions__codename='view_employee').exists()
        context['has_perm2'] = has_perm2
        
        return context
    
class EmployeeListView(LoginRequiredMixin,TemplateView):
    template_name = "users/employees.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['employees'] = Employee.objects.all()
        return context