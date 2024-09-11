
from django.urls import path
from .views import CreateEmployeeView, EmployeeUpdateView
#
urlpatterns = [
    path('create-employee/', CreateEmployeeView.as_view(), name='create-employee'),
    path('update-employee/<int:pk>/', EmployeeUpdateView.as_view(), name='update-employee'),

]
