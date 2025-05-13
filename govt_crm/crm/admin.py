from django.contrib import admin
from .models import FormData, TaskAssignment, TicketList
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


@admin.register(FormData)
class FormDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at', 'is_completed']
    search_fields = ['user__username', 'user__email']
    list_filter = ['created_at']


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assigned_to', 'district', 'taluka', 'region', 'tanda', 'deadline', 'additional_instructions', 'assigned_at', 'is_completed')
    list_filter = ('assigned_to', 'district', 'is_completed')
    search_fields = ('user__username', 'district')

@admin.register(TicketList)
class TicketListAdmin(admin.ModelAdmin):
    list_display = ('issue_type', 'title', 'description', 'status', 'created_at')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)