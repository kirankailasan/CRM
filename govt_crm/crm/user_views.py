from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import UserProfile, FormData, TaskAssignment, TicketList, ActivityLog
import random, json


def appoint_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'User ID is required.'})

        try:
            assigned_to = get_object_or_404(User, id=user_id)

            TaskAssignment.objects.create(
                assigned_to=assigned_to,
                district=request.POST.get('district'),
                taluka=request.POST.get('taluka'),
                region=request.POST.get('region'),
                tanda=request.POST.get('tanda'),
                deadline=request.POST.get('deadline'),
                additional_instructions=request.POST.get('additional')
            )

            return redirect("manage_users")
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



@login_required(login_url='/')
def dashboard(request):
    user = request.user
    assignments = TaskAssignment.objects.filter(assigned_to=user).order_by('-assigned_at')
    is_not_completed = assignments.filter(is_completed=False)
    is_completed = assignments.filter(is_completed=True)
    recent_activities = ActivityLog.objects.filter(user=request.user).order_by('-date')[:5]

    total_tasks = assignments.count()
    completed_tasks = is_completed.count()

    if total_tasks>0:
        performance = round((completed_tasks/total_tasks) * 100)
    else:
        performance =0

    return render(request, 'dashboard.html', {
        'assignments': assignments,
        'is_completed': is_completed,
        'is_not_completed': is_not_completed,
        'performance': performance,
        'recent_activities': recent_activities,
    
    })




def faqs(request):
    return render(request, 'faqs.html')

def tickets(request):
    if request.method == 'POST':
        issue_type = request.POST.get('category')
        title = request.POST.get('subject')
        description = request.POST.get('description')
        if issue_type and title and description:
            TicketList.objects.create(
                user=request.user,
                issue_type=issue_type,
                title=title,
                description=description,
                status='Open'
            )
            ActivityLog.objects.create(
                user=request.user,
                activity="Submitted a ticket",
                status="Completed",
                verb="Submit"
            )

        return redirect('tickets')
    user_tickets = TicketList.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'tickets.html', {'user_tickets': user_tickets})