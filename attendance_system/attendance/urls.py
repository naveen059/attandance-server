# attendance/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # API Endpoints
    path('register_employee/', views.register_employee_api, name='register_employee'),
    path('mark_attendance/', views.mark_attendance_api, name='mark_attendance'),

    # HTML Rendering Endpoints
    path('register_employee_page/', views.register_employee_page, name='register_employee_page'),
    path('mark_attendance_page/', views.mark_attendance_page, name='mark_attendance_page'),
]