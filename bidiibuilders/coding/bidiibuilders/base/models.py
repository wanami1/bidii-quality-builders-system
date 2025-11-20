from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# ==================== TEAM MODEL ====================
class Team(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ==================== PROJECT MODEL ====================
class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return f"{self.name} - {self.client_name or 'No Client'}"


# ==================== WORKER MODEL ====================
class Worker(models.Model):
    ROLE_CHOICES = [
        ('mason', 'Mason'),
        ('carpenter', 'Carpenter'),
        ('electrician', 'Electrician'),
        ('plumber', 'Plumber'),
        ('painter', 'Painter'),
        ('welder', 'Welder'),
        ('laborer', 'General Laborer'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'On Project'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]

    # Core fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='worker_profile')
    name = models.CharField(max_length=200)  # ⭐ Visible to client
    phone = models.CharField(max_length=20, blank=True, null=True)  # ⭐ Visible to client
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)  # ⭐ Visible to client (trade)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)  # ⭐ Visible to client
    
    # Staff Profile fields
    experience_years = models.IntegerField(default=0, blank=True, null=True)  # ⭐ Visible to client
    bio = models.TextField(blank=True, null=True)  # ⭐ Visible to client
    skills = models.JSONField(default=list, blank=True)  # ⭐ Visible to client - stores list of skills
    
    # Internal fields
    id_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    rating = models.DecimalField(max_digits=5, decimal_places=1, default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    completed_projects = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Worker'
        verbose_name_plural = 'Workers'

    def __str__(self):
        return f"{self.name} - {self.role}"
    
    def get_role_display_full(self):
        """Return full role name"""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)


# ==================== SKILL MODEL ====================
class Skill(models.Model):
    SKILL_CHOICES = [
        ('foundation', 'Foundation Work'),
        ('framing', 'Framing & Structure'),
        ('finishing', 'Finishing & Details'),
        ('wiring', 'Wiring & Installation'),
        ('plumbing', 'Plumbing Work'),
        ('painting', 'Painting & Decorating'),
        ('tile_work', 'Tile Work'),
        ('carpentry', 'Carpentry'),
        ('welding', 'Welding'),
        ('roofing', 'Roofing'),
    ]

    name = models.CharField(max_length=100, choices=SKILL_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.name


# ==================== PAYMENT MODEL ====================
class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('received', 'Income - Received'),
        ('paid', 'Expense - Paid'),
    ]

    CATEGORY_CHOICES = [
        ('client_payment', 'Client Payment'),
        ('worker_wages', 'Worker Wages'),
        ('materials', 'Materials'),
        ('equipment', 'Equipment Rental'),
        ('transport', 'Transport'),
        ('utilities', 'Utilities'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True, null=True)
    date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='mpesa')
    reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.type} - KES {self.amount} ({self.date})"


# ==================== TASK MODEL ====================
class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ('meeting', 'Meeting'),
        ('inspection', 'Inspection'),
        ('delivery', 'Delivery'),
        ('milestone', 'Milestone'),
        ('maintenance', 'Maintenance'),
        ('safety_check', 'Safety Check'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f"{self.title} - {self.date}"


# ==================== TEAM MEMBER MODEL ====================
class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('tester', 'Tester'),
        ('other', 'Other'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('team', 'user')
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f"{self.user.username} in {self.team.name} as {self.role}"


# ==================== JOB APPLICATION MODEL ====================
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='job_applications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    cover_letter = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('worker', 'project')
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'

    def __str__(self):
        return f"{self.worker.name} - {self.project.name} ({self.status})"

# ==================== TIME LOG MODEL ====================
class TimeLog(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='time_logs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='time_logs', null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    clock_in_time = models.DateTimeField(auto_now_add=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-clock_in_time']
        verbose_name = 'Time Log'
        verbose_name_plural = 'Time Logs'

    def save(self, *args, **kwargs):
        if self.clock_in_time and self.clock_out_time:
            delta = self.clock_out_time - self.clock_in_time
            self.hours_worked = round(delta.total_seconds() / 3600, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.worker.name} - {self.date} ({self.hours_worked or '?' } hrs)"

