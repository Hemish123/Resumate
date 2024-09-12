
from django.urls import path
from .views import CreateEmployeeView, UserUpdateView
#
urlpatterns = [
    path('create-employee/', CreateEmployeeView.as_view(), name='create-employee'),
    path('update-employee/<int:pk>/', UserUpdateView.as_view(), name='update-employee'),

]
