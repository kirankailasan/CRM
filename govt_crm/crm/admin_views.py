from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
import json
from .models import TaskAssignment, User, TicketList, UserProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test


def manage_users(request):
    user_completion_data = (
        TaskAssignment.objects.filter(is_completed=True)
        .values('assigned_to__username')
        .annotate(total_completed=Count('id'))
    )
    user_labels = [entry['assigned_to__username'] for entry in user_completion_data]
    user_data = [entry['total_completed'] for entry in user_completion_data]

    assignment = TaskAssignment.objects.all()
    users = UserProfile.objects.exclude(user__is_superuser=True)

    return render(request, 'admin/manage_users.html', {
        'user_labels_json': json.dumps(user_labels),
        'user_data_json': json.dumps(user_data),
        'users': users,
        'assignment': assignment,
    })


def admin_tickets(request):
    sort = request.GET.get('sort', 'created_at_desc')
    issue_type= request.GET.get('issue_type', '')
    status = request.GET.get('status', '')

    order_by = '-created_at'

    if sort == 'created_at_asc':
        order_by = 'created_at'

    user_tickets = TicketList.objects.select_related('user').all()

    if issue_type:
        user_tickets = user_tickets.filter(issue_type=issue_type)
    if status:
        user_tickets = user_tickets.filter(status=status)

    user_tickets = user_tickets.order_by(order_by)

    return render(request, 'admin/admin_tickets.html', {
        'user_tickets': user_tickets,
        'sort': sort,
        'selected_issue_type': issue_type,
        'selected_status': status,
    })

def close_ticket(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(TicketList, id=ticket_id)
        ticket.status = 'Closed'
        ticket.save()
    return redirect('admin_tickets')

from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

@login_required(login_url='admin_login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def create_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # Create UserProfile for the new user
            UserProfile.objects.create(user=user)
            return redirect('manage_users') 
        else:
            return render(request, 'admin/manage_users.html', {'error': 'Username already exists'})
    return render(request, 'admin/manage_users.html')