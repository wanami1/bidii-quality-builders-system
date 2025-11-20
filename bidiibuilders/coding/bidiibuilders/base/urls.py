from django.urls import path
from . import views

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main App
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/', views.projects, name='projects'),
    path('projects/delete/<int:id>/', views.delete_project, name='delete_project'),
    path('workers/', views.workers, name='workers'),
    path('workers/delete/<int:id>/', views.delete_worker, name='delete_worker'),
    path('payments/', views.payments, name='payments'),
    path('payments/delete/<int:id>/', views.delete_payment, name='delete_payment'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule/delete/<int:id>/', views.delete_task, name='delete_task'),
    path('schedule/complete/<int:id>/', views.complete_task, name='complete_task'),
    path('support/', views.support, name='support'),
    
    # Staff Portal
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/portal/', views.staff_portal, name='staff_portal'),
    path('staff/estimates/', views.staff_estimates, name='staff_estimates'),
    path('staff/projects/', views.staff_projects, name='staff_projects'),
    path('staff/workers/', views.staff_workers, name='staff_workers'),
    path('staff/materials/', views.staff_materials, name='staff_materials'),
    path('staff/schedule/', views.staff_schedule, name='staff_schedule'),
    path('staff/invoices/', views.staff_invoices, name='staff_invoices'),
    path('staff/payments/', views.staff_payments, name='staff_payments'),
    
    # Job Applications & Time Tracking
    path('apply-job/<int:project_id>/', views.apply_for_job, name='apply_for_job'),
    path('respond-application/<int:app_id>/', views.respond_to_application, name='respond_to_application'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
]