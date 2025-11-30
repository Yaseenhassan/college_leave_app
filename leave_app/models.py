from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Department(models.Model):
    """Department model for college departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class UserProfile(AbstractUser):
    """Enhanced User Model for College Staff"""
    
    # User type choices
    TEACHING = 'teaching'
    NON_TEACHING = 'non_teaching'
    USER_TYPE_CHOICES = [
        (TEACHING, 'Teaching Staff'),
        (NON_TEACHING, 'Non-Teaching Staff'),
    ]
    
    # Role choices
    TEACHER = 'teacher'
    HOD = 'hod'
    PRINCIPAL = 'principal'
    SUPERINTENDENT = 'superintendent'
    TEACHING_ADMIN = 'teaching_admin'
    NON_TEACHING_ADMIN = 'non_teaching_admin'
    ROLE_CHOICES = [
        (TEACHER, 'Teacher'),
        (HOD, 'Head of Department'),
        (PRINCIPAL, 'Principal'),
        (SUPERINTENDENT, 'Superintendent'),
        (TEACHING_ADMIN, 'Teaching Administrator'),
        (NON_TEACHING_ADMIN, 'Non-Teaching Administrator'),
    ]
    
    # Custom fields for college staff
    pen_number = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='PEN Number',
        null=True,
        blank=True
    )
    designation = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='staff'
    )
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default=TEACHING
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default=TEACHER
    )
    phone_number = models.CharField(max_length=15, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'
        ordering = ['department', 'designation', 'first_name']
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.designation} ({self.pen_number})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class LeaveApplication(models.Model):
    """Leave Application Model"""
    
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('vacation', 'Vacation Leave'),
        ('personal', 'Personal Leave'),
        ('duty', 'Duty Leave'),  # NEW: Non-deductible leave
    ]
    
    SESSION_CHOICES = [
        ('forenoon', 'Forenoon'),
        ('afternoon', 'Afternoon'),
        ('full_day', 'Full Day'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Application details
    applicant = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE,
        related_name='leave_applications'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    session = models.CharField(max_length=20, choices=SESSION_CHOICES, default='full_day')
    reason = models.TextField(null=True)
    applied_date = models.DateTimeField(auto_now_add=True)
    
    # Document upload
    supporting_document = models.FileField(
        upload_to='leave_documents/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Supporting Document (if any)'
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Approval workflow
    approved_by_hod = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hod_approved_leaves'
    )
    approved_by_principal = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='principal_approved_leaves'
    )
    hod_approval_date = models.DateTimeField(null=True, blank=True)
    principal_approval_date = models.DateTimeField(null=True, blank=True)
    
    # Comments
    hod_comments = models.TextField(blank=True)
    principal_comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-applied_date']
        verbose_name = 'Leave Application'
        verbose_name_plural = 'Leave Applications'
    
    def __str__(self):
        return f"{self.applicant} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def get_duration(self):
        """Calculate leave duration in days"""
        delta = self.end_date - self.start_date
        return delta.days + 1  # Inclusive of both start and end dates

class LeaveBalance(models.Model):
    """Track leave balances for each staff member"""
    
    staff = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.CharField(max_length=20, choices=LeaveApplication.LEAVE_TYPES)
    balance_days = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    academic_year = models.CharField(max_length=9)  # Format: 2024-2025
    
    class Meta:
        unique_together = ['staff', 'leave_type', 'academic_year']
        verbose_name = 'Leave Balance'
        verbose_name_plural = 'Leave Balances'
    
    def __str__(self):
        return f"{self.staff} - {self.leave_type}: {self.balance_days} days"