from django.contrib import admin

# Register your models here.
from .models import Employee, Company


class CompanyAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(users__user=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.company = request.user.employee.company
        super().save_model(request, obj, form, change)


admin.site.register(Company, CompanyAdmin)
admin.site.register(Employee)

