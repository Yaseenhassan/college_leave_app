from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Department, UserProfile, LeaveApplication, LeaveBalance

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'staff_count']
    search_fields = ['name', 'code']
    list_per_page = 20
    
    def staff_count(self, obj):
        return obj.staff.count()
    staff_count.short_description = 'Staff Count'

@admin.register(UserProfile)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'pen_number', 'get_full_name', 'designation', 'department', 'user_type', 'role']
    list_filter = ['user_type', 'role', 'department', 'is_active']
    search_fields = ['username', 'pen_number', 'first_name', 'last_name', 'email']
    list_per_page = 25
    
    fieldsets = UserAdmin.fieldsets + (
        ('College Information', {
            'fields': (
                'pen_number', 
                'designation', 
                'department', 
                'user_type', 
                'role',
                'phone_number'
            )
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'applicant', 
        'leave_type', 
        'start_date', 
        'end_date', 
        'session', 
        'status',
        'applied_date'
    ]
    list_filter = ['leave_type', 'status', 'session', 'applied_date']
    search_fields = ['applicant__first_name', 'applicant__last_name', 'applicant__pen_number']
    readonly_fields = ['applied_date']
    list_per_page = 25

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'balance_days', 'academic_year']
    list_filter = ['leave_type', 'academic_year']
    search_fields = ['staff__first_name', 'staff__last_name', 'staff__pen_number']
    list_per_page = 25