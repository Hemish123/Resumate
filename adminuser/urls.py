
from django.urls import path
from .views import CreateEmployeeView
#
urlpatterns = [
    path('create-employee/', CreateEmployeeView.as_view(), name='create-employee'),
]
