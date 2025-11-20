from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from .models import Project, Worker, Payment, Task, Skill, JobApplication, TimeLog


def home(request):
    return render(request, 'base/home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'base/home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('home')
    
    return render(request, 'base/register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login_view')
def dashboard(request):
    user_projects = Project.objects.filter(user=request.user).order_by('-created_at')
    user_workers = Worker.objects.filter(user=request.user)
    user_payments = Payment.objects.filter(user=request.user).order_by('-date')
    user_tasks = Task.objects.filter(user=request.user).order_by('date')
    
    today = datetime.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_week_end = this_week_start + timedelta(days=6)

    context = {
        'projects': user_projects,
        'projects_count': user_projects.count(),
        'completed_projects': user_projects.filter(status='completed').count(),
        'active_projects': user_projects.filter(status='active').count(),
        'pending_projects': user_projects.filter(status='planning').count(),
        'total_budget': user_projects.aggregate(Sum('budget'))['budget__sum'] or 0,
        'recent_projects': user_projects[:3],

        'workers': user_workers,
        'total_workers': user_workers.count(),
        'available_workers': user_workers.filter(status='available').count(),
        'on_project_workers': user_workers.filter(status='busy').count(),

        'payments': user_payments,
        'monthly_payments': user_payments.filter(
            date__year=today.year, date__month=today.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'received_payments': user_payments.filter(type='received').aggregate(Sum('amount'))['amount__sum'] or 0,
        'pending_payments': user_payments.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0,
        'recent_payments': user_payments[:4],

        'tasks': user_tasks,
        'tasks_this_week': user_tasks.filter(date__gte=this_week_start, date__lte=this_week_end).count(),
        'upcoming_tasks': user_tasks.filter(date__gte=today, completed=False)[:3],
    }
    return render(request, 'base/dashboard.html', context)


@login_required(login_url='login_view')
def projects(request):
    if request.method == 'POST':
        Project.objects.create(
            user=request.user,
            name=request.POST['name'],
            location=request.POST['location'],
            client_name=request.POST['client_name'],
            client_phone=request.POST['client_phone'],
            budget=request.POST['budget'],
            description=request.POST['description'],
            status=request.POST['status'],
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            progress=request.POST.get('progress', 0)
        )
        messages.success(request, 'Project created successfully!')
        return redirect('projects')
    
    user_projects = Project.objects.filter(user=request.user).order_by('-created_at')
    user_applications = JobApplication.objects.filter(project__user=request.user).order_by('-applied_at')
    
    context = {
        'projects': user_projects,
        'applications': user_applications,
        'total_projects': user_projects.count(),
        'active_projects': user_projects.filter(status='active').count(),
        'planning_projects': user_projects.filter(status='planning').count(),
        'completed_projects': user_projects.filter(status='completed').count(),
    }
    return render(request, 'base/projects.html', context)


@login_required(login_url='login_view')
def delete_project(request, id):
    project = get_object_or_404(Project, id=id, user=request.user)
    project.delete()
    messages.success(request, 'Project deleted successfully!')
    return redirect('projects')


@login_required(login_url='login_view')
def workers(request):
    all_workers = Worker.objects.all().order_by('-rating', 'name')
    
    trade_filter = request.GET.get('trade', '')
    status_filter = request.GET.get('status', '')
    
    if trade_filter:
        all_workers = all_workers.filter(role=trade_filter)
    
    if status_filter:
        all_workers = all_workers.filter(status=status_filter)
    
    context = {
        'workers': all_workers,
        'total_workers': Worker.objects.count(),
        'available_workers': Worker.objects.filter(status='available').count(),
        'on_project_workers': Worker.objects.filter(status='busy').count(),
    }
    
    return render(request, 'base/workers.html', context)


@login_required(login_url='login_view')
def delete_worker(request, id):
    worker = get_object_or_404(Worker, id=id, user=request.user)
    worker.delete()
    messages.success(request, 'Worker deleted successfully!')
    return redirect('workers')


@login_required(login_url='login_view')
def payments(request):
    if request.method == 'POST':
        Payment.objects.create(
            user=request.user,
            type=request.POST['type'],
            category=request.POST['category'],
            amount=request.POST['amount'],
            description=request.POST['description'],
            date=request.POST['date'],
            status=request.POST.get('status', 'completed'),
            payment_method=request.POST.get('payment_method', 'mpesa')
        )
        messages.success(request, 'Payment recorded successfully!')
        return redirect('payments')
    
    user_payments = Payment.objects.filter(user=request.user).order_by('-date')
    today = datetime.now().date()
    
    context = {
        'payments': user_payments,
        'total_received': user_payments.filter(type='received').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_pending': user_payments.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_paid': user_payments.filter(type='paid').aggregate(Sum('amount'))['amount__sum'] or 0,
        'monthly_total': user_payments.filter(date__year=today.year, date__month=today.month).aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    return render(request, 'base/payment.html', context)


@login_required(login_url='login_view')
def delete_payment(request, id):
    payment = get_object_or_404(Payment, id=id, user=request.user)
    payment.delete()
    messages.success(request, 'Payment deleted successfully!')
    return redirect('payments')


@login_required(login_url='login_view')
def schedule(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        project = None
        if project_id:
            project = get_object_or_404(Project, id=project_id, user=request.user)
        
        Task.objects.create(
            user=request.user,
            title=request.POST['title'],
            type=request.POST['type'],
            date=request.POST['date'],
            time=request.POST['time'],
            description=request.POST.get('description', ''),
            project=project,
            priority=request.POST.get('priority', 'medium'),
            completed=False
        )
        messages.success(request, 'Task added successfully!')
        return redirect('schedule')
    
    user_tasks = Task.objects.filter(user=request.user).order_by('date')
    user_projects = Project.objects.filter(user=request.user)
    
    today = datetime.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_week_end = this_week_start + timedelta(days=6)
    
    context = {
        'tasks': user_tasks,
        'projects': user_projects,
        'upcoming_count': user_tasks.filter(date__gte=today, completed=False).count(),
        'this_week_count': user_tasks.filter(date__gte=this_week_start, date__lte=this_week_end, completed=False).count(),
        'overdue_count': user_tasks.filter(date__lt=today, completed=False).count(),
        'completed_count': user_tasks.filter(completed=True).count(),
    }
    return render(request, 'base/schedule.html', context)


@login_required(login_url='login_view')
def delete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect('schedule')


@login_required(login_url='login_view')
def complete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.completed = True
    task.save()
    messages.success(request, 'Task marked as completed!')
    return redirect('schedule')


@login_required(login_url='login_view')
def support(request):
    return render(request, 'base/support.html')


def staff_login(request):
    if request.user.is_authenticated:
        # If already authenticated, redirect appropriately instead of logging out
        if request.user.is_staff:
            return redirect('staff_portal')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('staff_portal')
            else:
                messages.error(request, 'This account does not have staff access. Please use the main login.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'base/staff_login.html')


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
def staff_portal(request):
    if request.method == 'POST':
        worker, created = Worker.objects.get_or_create(user=request.user)
        
        worker.name = request.POST.get('full_name', worker.name)
        worker.phone = request.POST.get('phone', worker.phone)
        worker.role = request.POST.get('trade', worker.role)
        worker.daily_rate = request.POST.get('daily_rate', worker.daily_rate)
        worker.experience_years = int(request.POST.get('experience', 0)) if request.POST.get('experience') else 0
        worker.bio = request.POST.get('bio', worker.bio)
        worker.status = request.POST.get('status', 'available')
        
        skills = request.POST.getlist('skills')
        worker.skills = skills
        
        worker.save()
        messages.success(request, '✅ Profile updated successfully!')
        return redirect('staff_portal')
    
    try:
        worker_profile = Worker.objects.get(user=request.user)
    except Worker.DoesNotExist:
        worker_profile = None
    
    # Show only active projects as available work for workers
    available_jobs = Project.objects.filter(status='active').order_by('-created_at')
    all_workers = Worker.objects.exclude(user=request.user).order_by('-rating')
    
    # Get tasks assigned to this worker
    my_work = Task.objects.filter(user=request.user).order_by('date')
    
    context = {
        'staff_name': request.user.get_full_name() or request.user.username,
        'worker_profile': worker_profile,
        'available_jobs': available_jobs,
        'workers': all_workers,
        'my_work': my_work,
        'my_assignments': available_jobs.filter(user=request.user)[:3] if worker_profile else [],
        'available_count': available_jobs.count(),
        'skills': dict(Skill.SKILL_CHOICES),
        'title': 'WorkerPortal',  # Add title to avoid template errors
    }
    
    return render(request, 'base/staff.html', context)


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
def staff_estimates(request):
    context = {
        'title': 'Estimates',
    }
    return render(request, 'base/staff.html', context)


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
def staff_projects(request):
    projects = Project.objects.all().order_by('-created_at')
    context = {
        'projects': projects,
        'title': 'Projects',
        'active_count': projects.filter(status='active').count(),
        'completed_count': projects.filter(status='completed').count(),
    }
    return render(request, 'base/staff.html', context)


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
def staff_workers(request):
    workers = Worker.objects.all().order_by('-rating')
    context = {
        'workers': workers,
        'title': 'Workers',
        'available_count': workers.filter(status='available').count(),
        'busy_count': workers.filter(status='busy').count(),
        'total_count': workers.count(),
    }
    return render(request, 'base/staff.html', context)


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
def staff_materials(request):
    context = {
        'title': 'Materials',
    }
    return render(request, 'base/staff.html', context)


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
def staff_schedule(request):
    tasks = Task.objects.all().order_by('date')
    today = datetime.now().date()
    context = {
        'tasks': tasks,
        'title': 'Schedule',
        'upcoming_tasks': tasks.filter(date__gte=today).count(),
        'overdue_tasks': tasks.filter(date__lt=today, completed=False).count(),
    }
    return render(request, 'base/staff.html', context)


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
def staff_invoices(request):
    context = {
        'title': 'Invoices',
    }
    return render(request, 'base/staff.html', context)


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
def staff_payments(request):
    payments = Payment.objects.all().order_by('-date')
    context = {
        'payments': payments,
        'title': 'Payments',
        'total_received': payments.filter(type='received').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_paid': payments.filter(type='paid').aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    return render(request, 'base/staff.html', context)


# ==================== JOB APPLICATION HANDLERS ====================
@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
@require_http_methods(["POST"])
def apply_for_job(request, project_id):
    """Worker applies for a project"""
    try:
        project = get_object_or_404(Project, id=project_id)
        worker = get_object_or_404(Worker, user=request.user)
        
        # Check if already applied
        app, created = JobApplication.objects.get_or_create(
            worker=worker,
            project=project,
            defaults={'cover_letter': request.POST.get('cover_letter', '')}
        )
        
        if created:
            messages.success(request, f'✅ Applied for {project.name}!')
            return JsonResponse({'status': 'success', 'message': 'Application submitted'})
        else:
            return JsonResponse({'status': 'info', 'message': 'Already applied for this project'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required(login_url='login_view')
@require_http_methods(["POST"])
def respond_to_application(request, app_id):
    """Client accepts or rejects worker application"""
    try:
        app = get_object_or_404(JobApplication, id=app_id, project__user=request.user)
        action = request.POST.get('action', 'accept')  # accept or reject
        
        app.status = 'accepted' if action == 'accept' else 'rejected'
        app.responded_at = datetime.now()
        app.notes = request.POST.get('notes', '')
        app.save()
        
        status_text = 'Accepted' if action == 'accept' else 'Rejected'
        messages.success(request, f'✅ Application {status_text}!')
        return redirect('projects')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('projects')


# ==================== TIME LOG HANDLERS ====================
@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
@require_http_methods(["POST"])
def clock_in(request):
    """Worker clocks in"""
    try:
        worker = get_object_or_404(Worker, user=request.user)
        project_id = request.POST.get('project_id')
        project = None
        
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                pass
        
        today = datetime.now().date()
        
        # Check if already clocked in today
        existing = TimeLog.objects.filter(
            worker=worker,
            date=today,
            clock_out_time__isnull=True
        ).first()
        
        if existing:
            return JsonResponse({'status': 'info', 'message': 'Already clocked in'})
        
        time_log = TimeLog.objects.create(
            worker=worker,
            project=project,
            date=today,
            clock_in_time=datetime.now()
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'✅ Clocked in at {datetime.now().strftime("%H:%M:%S")}',
            'time_log_id': time_log.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required(login_url='staff_login')
@user_passes_test(lambda u: u.is_staff, login_url='staff_login')
@require_http_methods(["POST"])
def clock_out(request):
    """Worker clocks out"""
    try:
        worker = get_object_or_404(Worker, user=request.user)
        today = datetime.now().date()
        
        # Find active time log
        time_log = TimeLog.objects.filter(
            worker=worker,
            date=today,
            clock_out_time__isnull=True
        ).first()
        
        if not time_log:
            return JsonResponse({'status': 'info', 'message': 'No active clock in found'})
        
        time_log.clock_out_time = datetime.now()
        time_log.notes = request.POST.get('notes', '')
        time_log.save()
        
        hours = time_log.hours_worked or 0
        return JsonResponse({
            'status': 'success',
            'message': f'✅ Clocked out at {datetime.now().strftime("%H:%M:%S")} ({hours} hrs)',
            'hours_worked': float(hours)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)