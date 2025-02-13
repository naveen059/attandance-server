from django.urls import path
from . import views

urlpatterns = [
    path('register_employee/', views.register_employee, name='register_employee'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
]