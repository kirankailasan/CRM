from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import random, json
from .models import UserProfile, FormData, TaskAssignment, ActivityLog
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import logging
logger = logging.getLogger(__name__)
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Count


# store OTPs temporarily (for now, in-memory)
email_otp_map = {}

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        otp = str(random.randint(100000, 999999))
        email_otp_map[email] = otp

        send_mail(
            'Your OTP Verification Code',
            f'Your OTP code is: {otp}',
            'randorer5@gmail.com',
            [email],
            fail_silently=False,
        )

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')

        if email_otp_map.get(email) == otp:
            del email_otp_map[email]
            return JsonResponse({'verified': True})
        return JsonResponse({'verified': False})
    return JsonResponse({'verified': False})






def register(request):
    if request.method == 'POST':
        first = request.POST.get('first_name')
        last = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        aadhaar = request.POST.get('aadhaar')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        address = request.POST.get('address')
        state = request.POST.get('state')
        district = request.POST.get('district')
        city = request.POST.get('city')
        profile_pic = request.FILES.get('profile_pic')

        if password != confirm:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=email).exists():
            return render(request, 'register.html', {'error': 'User already exists'})

        user = User.objects.create_user(username=email, email=email, password=password,
                                        first_name=first, last_name=last)

        profile = UserProfile.objects.create(
            user=user,
            phone=phone,
            aadhaar=aadhaar,
            address=address,
            state=state,
            district=district,
            city=city,
            profile_pic=profile_pic
        )

        request.session['prefill_email'] = email
        request.session['prefill_password'] = password
        request.session['auto_login_popup'] = True
        return redirect('index')

    return render(request, 'register.html')


def index(request):
    prefill_email = request.session.pop('prefill_email', '')
    prefill_password = request.session.pop('prefill_password', '')
    auto_login_popup = request.session.pop('auto_login_popup', False)

    return render(request, 'index.htm', {
        'prefill_email': prefill_email,
        'prefill_password': prefill_password,
        'auto_login_popup': auto_login_popup,
    })

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('index')




@csrf_exempt  
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "redirect_url": "/dashboard/"})
        else:
            return JsonResponse({"success": False, "message": "Invalid credentials"})
    return JsonResponse({"success": False, "message": "Only POST allowed"})

def morph_effect(request):
    return render(request, 'morph.htm')


def check_all(request):
    email = request.GET.get('email')
    phone = request.GET.get('phone')
    aadhaar = request.GET.get('aadhaar')

    if email:
        exists = UserProfile.objects.filter(email=email).exists()
        return JsonResponse({'exists': exists})

    if phone:
        exists = UserProfile.objects.filter(phone=phone).exists()
        return JsonResponse({'exists': exists})

    if aadhaar:
        exists = UserProfile.objects.filter(aadhaar=aadhaar).exists()
        return JsonResponse({'exists': exists})

    return JsonResponse({'error': 'No valid parameter provided'}, status=400)



def scheme_detail(request):
    return render(request, 'scheme_detail.html')



def all_forms(request):
    return render(request, 'all_forms.html' )


@login_required
def save_form_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Clean out CSRF token and other unnecessary fields
            form1_data = {key: value for key, value in data.get('form1_data', {}).items()}
            form2_data = {key: value for key, value in data.get('form2_data', {}).items()}
            form3_data = {key: value for key, value in data.get('form3_data', {}).items()}
            form4_data = {key: value for key, value in data.get('form4_data', {}).items()}
            form5_data = {key: value for key, value in data.get('form5_data', {}).items()}
            form6_data = {key: value for key, value in data.get('form6_data', {}).items()}
            form7_data = {key: value for key, value in data.get('form7_data', {}).items()}

            task = TaskAssignment.objects.filter(assigned_to=request.user, is_completed=False).last()

            # Create a new FormData entry
            form_data = FormData.objects.create(
                user=request.user,
                form1_data=form1_data,
                form2_data=form2_data,
                form3_data=form3_data,
                form4_data=form4_data,
                form5_data=form5_data,
                form6_data=form6_data,
                form7_data=form7_data, 
                task=task,
                is_completed=True
                
            )
            taluka_name = task.taluka if task and task.taluka else "Unknown Taluka"

            ActivityLog.objects.create(
                user=request.user,
                activity=f"Submitted form for ({taluka_name})",
                status="Completed",
                verb="Submit"
            )

            form_data.is_completed = True
            form_data.save()
            
            if task:
                task.is_completed = True
                task.save()
            
            # Return success response
            return JsonResponse({'message': 'All form data saved successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)




@login_required
def view_submitted_data(request):
    try:
        # Fetch all submitted entries by the current user (latest first)
        submitted_data = FormData.objects.filter(user=request.user).order_by('-created_at')

        if not submitted_data.exists():
            messages.error(request, 'No form data found for your account.')
            return redirect('dashboard')

        return render(request, 'submitted_data.html', {
            'submitted_data': submitted_data
        })

    except Exception as e:
        messages.error(request, f'Error fetching submitted data: {e}')
        return redirect('dashboard')
    


from django.template.loader import render_to_string




@login_required
def view_form_popup(request, form_id):
    try:
        # Allow superuser to view any form, users only their own
        if request.user.is_superuser:
            form_data = FormData.objects.get(id=form_id)
        else:
            form_data = FormData.objects.get(id=form_id, user=request.user)

        form1_data = form_data.form1_data or {}
        form4_data = form_data.form4_data or {}
        form5_data = form_data.form5_data or []
        form6_data = form_data.form6_data or {}
        form7_data = form_data.form7_data or {}
        number_range = range(1, 19)

        # --- Form 3 Display ---
        form3_data = []
        if isinstance(form_data.form3_data, list):
            form3_data = form_data.form3_data
        else:
            i = 1
            while True:
                name = form_data.form3_data.get(f'name_{i}')
                designation = form_data.form3_data.get(f'designation_{i}')
                contact = form_data.form3_data.get(f'contact_{i}')
                if not name and not designation and not contact:
                    break
                form3_data.append({
                    'name': name,
                    'designation': designation,
                    'contact': contact
                })
                i += 1

        # --- Form 5 Display ---
        form5_display = []
        if isinstance(form5_data, list):
            form5_display = form5_data
        else:
            i = 1
            while True:
                name = form5_data.get(f'name_{i}')
                position = form5_data.get(f'position_{i}')
                contact = form5_data.get(f'contact_{i}')
                if not name and not position and not contact:
                    break
                form5_display.append({
                    'name': name,
                    'position': position,
                    'contact': contact
                })
                i += 1

        form4_display = {
            'school_primary': form4_data.get('school_primary', ''),
            'school_secondary': form4_data.get('school_secondary', ''),
            'college_distance': form4_data.get('college_distance', ''),
            'bus_stand': form4_data.get('bus_stand', ''),
            'health_center': form4_data.get('health_center', ''),
            'veterinary_disp': form4_data.get('veterinary_disp', ''),
            'livestock_count': form4_data.get('livestock_count', ''),
            'has_milk_center': form4_data.get('has_milk_center', ''),
            'milk_center_name': form4_data.get('milk_center_name', ''),
            'milk_center_number': form4_data.get('milk_center_number', ''),
            'cattle_details': form4_data.get('cattle_details', ''),
            'shed_name': form4_data.get('shed_name', ''),
            'shed_number': form4_data.get('shed_number', ''),
            'electricity': form4_data.get('electricity', ''),
            'ration_shop': form4_data.get('ration_shop', ''),
            'ration_name': form4_data.get('ration_name', ''),
            'ration_number': form4_data.get('ration_number', ''),
            'water': form4_data.get('water', ''),
            'water_name': form4_data.get('water_name', ''),
            'water_number': form4_data.get('water_number', ''),
            'fpo': form4_data.get('fpo', ''),
            'fpo_name': form4_data.get('fpo_name', ''),
            'fpo_number': form4_data.get('fpo_number', ''),
            'hall': form4_data.get('hall', ''),
            'hall_name': form4_data.get('hall_name', ''),
            'hall_number': form4_data.get('hall_number', ''),
        }

        tanda_count = sum(1 for key in form1_data if key.startswith('tanda-name-'))
        if isinstance(form7_data.get('important_people'), list):
            important_people = form7_data['important_people']
        else:
            important_people = []
            i = 1
            while True:
                name = form7_data.get(f'important_person_name_{i}', '')
                designation = form7_data.get(f'important_designation_{i}', '')
                number = form7_data.get(f'important_person_number_{i}', '')
                if not name and not designation and not number:
                    break
                important_people.append({
                    'name': name,
                    'designation': designation,
                    'number': number
                })
                i += 1

        # --- Committee Members ---
        if isinstance(form7_data.get('committee_members'), list):
            committee_members = form7_data['committee_members']
        else:
            committee_members = []
            i = 1
            while True:
                name = form7_data.get(f'committee_member_name_{i}', '')
                designation = form7_data.get(f'committee_member_designation_{i}', '')
                contact = form7_data.get(f'committee_member_contact_{i}', '')
                address = form7_data.get(f'committee_member_address_{i}', '')
                email = form7_data.get(f'committee_member_email_{i}', '')
                dob = form7_data.get(f'committee_member_dob_{i}', '')
                if not name and not designation and not contact and not address and not email and not dob:
                    break
                committee_members.append({
                    'name': name,
                    'designation': designation,
                    'contact': contact,
                    'address': address,
                    'email': email,
                    'dob': dob
                })
                i += 1

        # --- Development Works ---
        if isinstance(form7_data.get('development_works'), list):
            development_works = form7_data['development_works']
        else:
            development_works = []
            i = 1
            while True:
                name = form7_data.get(f'name_of_work_{i}', '')
                status = form7_data.get(f'status_{i}', '')
                nature = form7_data.get(f'nature_of_work_{i}', '')
                fund = form7_data.get(f'fund_provision_{i}', '')
                if not name and not status and not nature and not fund:
                    break
                development_works.append({
                    'name': name,
                    'status': status,
                    'nature': nature,
                    'fund': fund
                })
                i += 1

        # --- Temples ---
        if isinstance(form7_data.get('temple_list'), list):
            temple_list = form7_data['temple_list']
        else:
            temple_list = []
            i = 1
            while True:
                name = form7_data.get(f'temple_name_{i}', '')
                place = form7_data.get(f'temple_place_{i}', '')
                location = form7_data.get(f'temple_location_{i}', '')
                area = form7_data.get(f'temple_area_{i}', '')
                proposal = form7_data.get(f'temple_proposal_{i}', '')
                funding = form7_data.get(f'temple_funding_{i}', '')
                if not name and not place and not location and not area and not proposal and not funding:
                    break
                temple_list.append({
                    'name': name,
                    'place': place,
                    'location': location,
                    'area': area,
                    'proposal': proposal,
                    'funding': funding
                })
                i += 1

        # --- Choir (Bhajani Mandal) ---
        if isinstance(form7_data.get('choir_list'), list):
            choir_list = form7_data['choir_list']
        else:
            choir_list = []
            i = 1
            while True:
                name = form7_data.get(f'choir_name_{i}', '')
                members = form7_data.get(f'members_{i}', '')
                members_name = form7_data.get(f'members_name_{i}', '')
                contact_no = form7_data.get(f'contact_no_{i}', '')
                address = form7_data.get(f'address_{i}', '')
                if not name and not members and not members_name and not contact_no and not address:
                    break
                choir_list.append({
                    'name': name,
                    'members': members,
                    'members_name': members_name,
                    'contact_no': contact_no,
                    'address': address
                })
                i += 1

        context = {
            'form1_data': form1_data,
            'form3_data': form3_data,
            'form2_data': form_data.form2_data,
            'form4_data': form4_display,
            'form5_data': form5_display,
            'number_range': number_range,
            'form6_data': form_data.form6_data,
            'form7_data': form7_data,
            'tanda_count': tanda_count,
            'development_works':development_works,
            'committee_members': committee_members,
            'temple_list':temple_list,
            'important_people': important_people,
            'choir_list': choir_list,
            'user': request.user,  # <-- Add this for template logic if needed
            
        }

        html = render_to_string('forms/submitted_form.html', context, request=request)
        return JsonResponse({'html': html})

    except FormData.DoesNotExist:
        return JsonResponse({'error': 'Form data not found'}, status=404)








'''@csrf_exempt
def handle_form(request, form_number):
    template_name = f'form{form_number}.html'
    form_key = f'form{form_number}'

    if request.method == 'POST':
        # Handle form saving
        if request.POST.get('save_form') == form_key:
            form_data = {
                key: value for key, value in request.POST.items()
                if key not in ['csrfmiddlewaretoken', 'save_form']
            }

            # Store form data in session
            request.session[form_key] = form_data
            request.session.modified = True

            return render(request, template_name, {
                'message': 'Saved successfully!',
                'form_data': form_data
            })



    # Load existing session data if available (optional)
    form_data = request.session.get(form_key, {})
    return render(request, template_name, {'form_data': form_data})'''







#admin part 

def is_superuser(user):
    return user.is_superuser


@csrf_exempt
def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid email or password'})

        user = authenticate(username=user.username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid email or password'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

from django.db.models import Sum, F
from django.db.models.functions import Cast
from django.db import models

@login_required(login_url='admin_login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_dashboard(request):
    total_tandas = TaskAssignment.objects.aggregate(total=Sum('tanda'))['total'] or 0

    total_population = FormData.objects.filter(is_completed=True).aggregate(
        total=Sum(Cast(F('form1_data__total-population-1'), output_field=models.IntegerField()))
    )['total'] or 0

    total_housing_demand = FormData.objects.filter(is_completed=True).aggregate(
        total=Sum(
            Cast(F('form2_data__houses_sanctioned'), output_field=models.IntegerField()) +
            Cast(F('form2_data__houses_remaining'), output_field=models.IntegerField())
        )
    )['total'] or 0

    approved_houses = FormData.objects.filter(is_completed=True).aggregate(
        total=Sum(Cast(F('form2_data__houses_sanctioned'), output_field=models.IntegerField()))
    )['total'] or 0

    completed_works = TaskAssignment.objects.filter(is_completed=True).count()

    # Chart data
    district_data = TaskAssignment.objects.filter(is_completed=True).values('district').annotate(total_tandas=Sum('tanda'))

    labels = [entry['district'] for entry in district_data]
    data = [entry['total_tandas'] for entry in district_data]
    total_tandas = sum(data) or 1  # Avoid division by zero
    percentages = [(tanda / total_tandas) * 100 for tanda in data]

    # Population data
    male = FormData.objects.filter(is_completed=True).aggregate(
        total_male=Sum(Cast(F('form1_data__male-1'), output_field=models.IntegerField()))
    )['total_male'] or 0

    female = FormData.objects.filter(is_completed=True).aggregate(
        total_female=Sum(Cast(F('form1_data__female-1'), output_field=models.IntegerField()))
    )['total_female'] or 0

    labels_population = ['Male', 'Female']
    data_population = [male, female]
    total_population_gender = sum(data_population) or 1  # Again, avoid division by zero
    percentages_population = [(pop / total_population_gender) * 100 for pop in data_population]

    # Tandas Completed by User
 
    user_completion_data = (
        TaskAssignment.objects.filter(is_completed=True)
        .values('assigned_to__username')
        .annotate(total_completed=Count('id'))
    )

    user_labels = [entry['assigned_to__username'] for entry in user_completion_data]
    user_data = [entry['total_completed'] for entry in user_completion_data]

    assignment = TaskAssignment.objects.all()
    users = UserProfile.objects.exclude(user__is_superuser=True)

    return render(request, 'admin_dashboard.html', {
        'users': users,
        'assignment': assignment,
        'total_tandas': total_tandas,
        'total_population': total_population,
        'total_housing_demand': total_housing_demand,
        'approved_houses': approved_houses,
        'completed_works': completed_works,
        'labels_json': json.dumps(labels),
        'data_json': json.dumps(data),
        'percentages_json': json.dumps([round(p) for p in percentages]),  # <-- rounded to 2 decimals
        'labels_population_json': json.dumps(labels_population),
        'data_population_json': json.dumps(data_population),
        'percentages_population_json': json.dumps([round(p) for p in percentages_population]),  # <-- rounded to NO decimal
        'user_labels_json': json.dumps(user_labels),
        'user_data_json': json.dumps(user_data),
    })



def admin_logout(request):
    logout(request)
    return redirect('index')


def get_user_details(request, user_id):
    from .models import UserProfile
    try:
        profile = UserProfile.objects.select_related('user').get(id=user_id)
        return JsonResponse({
            'name': f"{profile.user.first_name} {profile.user.last_name}",
            'email': profile.user.email,
            'phone': profile.phone,
            'aadhaar': profile.aadhaar,
            'address': profile.address,
            'state': profile.state,
            'district': profile.district,
            'city': profile.city,
            'profile_pic': profile.profile_pic.url if profile.profile_pic else '/static/images/user.png'
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    

def assign_task(request):
    task_name = request.GET.get('task_name', '')
    users = UserProfile.objects.exclude(user__is_superuser=True)

    # Get list of user IDs who are already assigned this task
    assigned_user_ids = TaskAssignment.objects.filter(form_name=task_name).values_list('user__id', flat=True)

    return render(request, 'admin/assign_task.html', {
        'users': users,
        'task_name': task_name,
        'assigned_user_ids': assigned_user_ids,
    })

def submit_assignment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        form_name = data.get('form_name')

        if user_id and form_name:
            user = User.objects.get(id=user_id)
            TaskAssignment.objects.create(user=user, form_name=form_name, assigned_by=request.user)
            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

def completed_works(request):
    submitted_data = FormData.objects.filter(is_completed=True).select_related('user')
    return render(request, 'admin/completed_works.html', {'submitted_data': submitted_data})

from xhtml2pdf import pisa
from django.template.loader import get_template

@login_required(login_url='admin_login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def download_form_pdf(request, form_id):
    try:
        # Allow superuser to view any form, users only their own
        if request.user.is_superuser:
            form_data = FormData.objects.get(id=form_id)
        else:
            form_data = FormData.objects.get(id=form_id, user=request.user)

        form1_data = form_data.form1_data or {}
        form4_data = form_data.form4_data or {}
        form5_data = form_data.form5_data or []
        form6_data = form_data.form6_data or {}
        form7_data = form_data.form7_data or {}
        number_range = range(1, 19)

        # --- Form 3 Display ---
        form3_data = []
        if isinstance(form_data.form3_data, list):
            form3_data = form_data.form3_data
        else:
            i = 1
            while True:
                name = form_data.form3_data.get(f'name_{i}')
                designation = form_data.form3_data.get(f'designation_{i}')
                contact = form_data.form3_data.get(f'contact_{i}')
                if not name and not designation and not contact:
                    break
                form3_data.append({
                    'name': name,
                    'designation': designation,
                    'contact': contact
                })
                i += 1

        # --- Form 5 Display ---
        form5_display = []
        if isinstance(form5_data, list):
            form5_display = form5_data
        else:
            i = 1
            while True:
                name = form5_data.get(f'name_{i}')
                position = form5_data.get(f'position_{i}')
                contact = form5_data.get(f'contact_{i}')
                if not name and not position and not contact:
                    break
                form5_display.append({
                    'name': name,
                    'position': position,
                    'contact': contact
                })
                i += 1

        form4_display = {
            'school_primary': form4_data.get('school_primary', ''),
            'school_secondary': form4_data.get('school_secondary', ''),
            'college_distance': form4_data.get('college_distance', ''),
            'bus_stand': form4_data.get('bus_stand', ''),
            'health_center': form4_data.get('health_center', ''),
            'veterinary_disp': form4_data.get('veterinary_disp', ''),
            'livestock_count': form4_data.get('livestock_count', ''),
            'has_milk_center': form4_data.get('has_milk_center', ''),
            'milk_center_name': form4_data.get('milk_center_name', ''),
            'milk_center_number': form4_data.get('milk_center_number', ''),
            'cattle_details': form4_data.get('cattle_details', ''),
            'shed_name': form4_data.get('shed_name', ''),
            'shed_number': form4_data.get('shed_number', ''),
            'electricity': form4_data.get('electricity', ''),
            'ration_shop': form4_data.get('ration_shop', ''),
            'ration_name': form4_data.get('ration_name', ''),
            'ration_number': form4_data.get('ration_number', ''),
            'water': form4_data.get('water', ''),
            'water_name': form4_data.get('water_name', ''),
            'water_number': form4_data.get('water_number', ''),
            'fpo': form4_data.get('fpo', ''),
            'fpo_name': form4_data.get('fpo_name', ''),
            'fpo_number': form4_data.get('fpo_number', ''),
            'hall': form4_data.get('hall', ''),
            'hall_name': form4_data.get('hall_name', ''),
            'hall_number': form4_data.get('hall_number', ''),
        }

        tanda_count = sum(1 for key in form1_data if key.startswith('tanda-name-'))
        if isinstance(form7_data.get('important_people'), list):
            important_people = form7_data['important_people']
        else:
            important_people = []
            i = 1
            while True:
                name = form7_data.get(f'important_person_name_{i}', '')
                designation = form7_data.get(f'important_designation_{i}', '')
                number = form7_data.get(f'important_person_number_{i}', '')
                if not name and not designation and not number:
                    break
                important_people.append({
                    'name': name,
                    'designation': designation,
                    'number': number
                })
                i += 1

        # --- Committee Members ---
        if isinstance(form7_data.get('committee_members'), list):
            committee_members = form7_data['committee_members']
        else:
            committee_members = []
            i = 1
            while True:
                name = form7_data.get(f'committee_member_name_{i}', '')
                designation = form7_data.get(f'committee_member_designation_{i}', '')
                contact = form7_data.get(f'committee_member_contact_{i}', '')
                address = form7_data.get(f'committee_member_address_{i}', '')
                email = form7_data.get(f'committee_member_email_{i}', '')
                dob = form7_data.get(f'committee_member_dob_{i}', '')
                if not name and not designation and not contact and not address and not email and not dob:
                    break
                committee_members.append({
                    'name': name,
                    'designation': designation,
                    'contact': contact,
                    'address': address,
                    'email': email,
                    'dob': dob
                })
                i += 1

        # --- Development Works ---
        if isinstance(form7_data.get('development_works'), list):
            development_works = form7_data['development_works']
        else:
            development_works = []
            i = 1
            while True:
                name = form7_data.get(f'name_of_work_{i}', '')
                status = form7_data.get(f'status_{i}', '')
                nature = form7_data.get(f'nature_of_work_{i}', '')
                fund = form7_data.get(f'fund_provision_{i}', '')
                if not name and not status and not nature and not fund:
                    break
                development_works.append({
                    'name': name,
                    'status': status,
                    'nature': nature,
                    'fund': fund
                })
                i += 1

        # --- Temples ---
        if isinstance(form7_data.get('temple_list'), list):
            temple_list = form7_data['temple_list']
        else:
            temple_list = []
            i = 1
            while True:
                name = form7_data.get(f'temple_name_{i}', '')
                place = form7_data.get(f'temple_place_{i}', '')
                location = form7_data.get(f'temple_location_{i}', '')
                area = form7_data.get(f'temple_area_{i}', '')
                proposal = form7_data.get(f'temple_proposal_{i}', '')
                funding = form7_data.get(f'temple_funding_{i}', '')
                if not name and not place and not location and not area and not proposal and not funding:
                    break
                temple_list.append({
                    'name': name,
                    'place': place,
                    'location': location,
                    'area': area,
                    'proposal': proposal,
                    'funding': funding
                })
                i += 1

        # --- Choir (Bhajani Mandal) ---
        if isinstance(form7_data.get('choir_list'), list):
            choir_list = form7_data['choir_list']
        else:
            choir_list = []
            i = 1
            while True:
                name = form7_data.get(f'choir_name_{i}', '')
                members = form7_data.get(f'members_{i}', '')
                members_name = form7_data.get(f'members_name_{i}', '')
                contact_no = form7_data.get(f'contact_no_{i}', '')
                address = form7_data.get(f'address_{i}', '')
                if not name and not members and not members_name and not contact_no and not address:
                    break
                choir_list.append({
                    'name': name,
                    'members': members,
                    'members_name': members_name,
                    'contact_no': contact_no,
                    'address': address
                })
                i += 1

        context = {
            'form1_data': form1_data,
            'form3_data': form3_data,
            'form2_data': form_data.form2_data,
            'form4_data': form4_display,
            'form5_data': form5_display,
            'number_range': number_range,
            'form6_data': form_data.form6_data,
            'form7_data': form7_data,
            'tanda_count': tanda_count,
            'development_works':development_works,
            'committee_members': committee_members,
            'temple_list':temple_list,
            'important_people': important_people,
            'choir_list': choir_list,
            'user': request.user,  # <-- Add this for template logic if needed
            
        }
        template = get_template('admin/submitted_form_download.html')
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="form_{form_id}.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    except FormData.DoesNotExist:
        return HttpResponse("Form not found.", status=404)


import openpyxl
from openpyxl.utils import get_column_letter


from bs4 import BeautifulSoup

@login_required(login_url='admin_login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def download_form_excel(request, form_id):
    try:
        # Allow superuser to view any form, users only their own
        if request.user.is_superuser:
            form_data = FormData.objects.get(id=form_id)
        else:
            form_data = FormData.objects.get(id=form_id, user=request.user)

        form1_data = form_data.form1_data or {}
        form4_data = form_data.form4_data or {}
        form5_data = form_data.form5_data or []
        form6_data = form_data.form6_data or {}
        form7_data = form_data.form7_data or {}
        number_range = range(1, 19)

        # --- Form 3 Display ---
        form3_data = []
        if isinstance(form_data.form3_data, list):
            form3_data = form_data.form3_data
        else:
            i = 1
            while True:
                name = form_data.form3_data.get(f'name_{i}')
                designation = form_data.form3_data.get(f'designation_{i}')
                contact = form_data.form3_data.get(f'contact_{i}')
                if not name and not designation and not contact:
                    break
                form3_data.append({
                    'name': name,
                    'designation': designation,
                    'contact': contact
                })
                i += 1

        # --- Form 5 Display ---
        form5_display = []
        if isinstance(form5_data, list):
            form5_display = form5_data
        else:
            i = 1
            while True:
                name = form5_data.get(f'name_{i}')
                position = form5_data.get(f'position_{i}')
                contact = form5_data.get(f'contact_{i}')
                if not name and not position and not contact:
                    break
                form5_display.append({
                    'name': name,
                    'position': position,
                    'contact': contact
                })
                i += 1

        form4_display = {
            'school_primary': form4_data.get('school_primary', ''),
            'school_secondary': form4_data.get('school_secondary', ''),
            'college_distance': form4_data.get('college_distance', ''),
            'bus_stand': form4_data.get('bus_stand', ''),
            'health_center': form4_data.get('health_center', ''),
            'veterinary_disp': form4_data.get('veterinary_disp', ''),
            'livestock_count': form4_data.get('livestock_count', ''),
            'has_milk_center': form4_data.get('has_milk_center', ''),
            'milk_center_name': form4_data.get('milk_center_name', ''),
            'milk_center_number': form4_data.get('milk_center_number', ''),
            'cattle_details': form4_data.get('cattle_details', ''),
            'shed_name': form4_data.get('shed_name', ''),
            'shed_number': form4_data.get('shed_number', ''),
            'electricity': form4_data.get('electricity', ''),
            'ration_shop': form4_data.get('ration_shop', ''),
            'ration_name': form4_data.get('ration_name', ''),
            'ration_number': form4_data.get('ration_number', ''),
            'water': form4_data.get('water', ''),
            'water_name': form4_data.get('water_name', ''),
            'water_number': form4_data.get('water_number', ''),
            'fpo': form4_data.get('fpo', ''),
            'fpo_name': form4_data.get('fpo_name', ''),
            'fpo_number': form4_data.get('fpo_number', ''),
            'hall': form4_data.get('hall', ''),
            'hall_name': form4_data.get('hall_name', ''),
            'hall_number': form4_data.get('hall_number', ''),
        }

        tanda_count = sum(1 for key in form1_data if key.startswith('tanda-name-'))
        if isinstance(form7_data.get('important_people'), list):
            important_people = form7_data['important_people']
        else:
            important_people = []
            i = 1
            while True:
                name = form7_data.get(f'important_person_name_{i}', '')
                designation = form7_data.get(f'important_designation_{i}', '')
                number = form7_data.get(f'important_person_number_{i}', '')
                if not name and not designation and not number:
                    break
                important_people.append({
                    'name': name,
                    'designation': designation,
                    'number': number
                })
                i += 1

        # --- Committee Members ---
        if isinstance(form7_data.get('committee_members'), list):
            committee_members = form7_data['committee_members']
        else:
            committee_members = []
            i = 1
            while True:
                name = form7_data.get(f'committee_member_name_{i}', '')
                designation = form7_data.get(f'committee_member_designation_{i}', '')
                contact = form7_data.get(f'committee_member_contact_{i}', '')
                address = form7_data.get(f'committee_member_address_{i}', '')
                email = form7_data.get(f'committee_member_email_{i}', '')
                dob = form7_data.get(f'committee_member_dob_{i}', '')
                if not name and not designation and not contact and not address and not email and not dob:
                    break
                committee_members.append({
                    'name': name,
                    'designation': designation,
                    'contact': contact,
                    'address': address,
                    'email': email,
                    'dob': dob
                })
                i += 1

        # --- Development Works ---
        if isinstance(form7_data.get('development_works'), list):
            development_works = form7_data['development_works']
        else:
            development_works = []
            i = 1
            while True:
                name = form7_data.get(f'name_of_work_{i}', '')
                status = form7_data.get(f'status_{i}', '')
                nature = form7_data.get(f'nature_of_work_{i}', '')
                fund = form7_data.get(f'fund_provision_{i}', '')
                if not name and not status and not nature and not fund:
                    break
                development_works.append({
                    'name': name,
                    'status': status,
                    'nature': nature,
                    'fund': fund
                })
                i += 1

        # --- Temples ---
        if isinstance(form7_data.get('temple_list'), list):
            temple_list = form7_data['temple_list']
        else:
            temple_list = []
            i = 1
            while True:
                name = form7_data.get(f'temple_name_{i}', '')
                place = form7_data.get(f'temple_place_{i}', '')
                location = form7_data.get(f'temple_location_{i}', '')
                area = form7_data.get(f'temple_area_{i}', '')
                proposal = form7_data.get(f'temple_proposal_{i}', '')
                funding = form7_data.get(f'temple_funding_{i}', '')
                if not name and not place and not location and not area and not proposal and not funding:
                    break
                temple_list.append({
                    'name': name,
                    'place': place,
                    'location': location,
                    'area': area,
                    'proposal': proposal,
                    'funding': funding
                })
                i += 1

        # --- Choir (Bhajani Mandal) ---
        if isinstance(form7_data.get('choir_list'), list):
            choir_list = form7_data['choir_list']
        else:
            choir_list = []
            i = 1
            while True:
                name = form7_data.get(f'choir_name_{i}', '')
                members = form7_data.get(f'members_{i}', '')
                members_name = form7_data.get(f'members_name_{i}', '')
                contact_no = form7_data.get(f'contact_no_{i}', '')
                address = form7_data.get(f'address_{i}', '')
                if not name and not members and not members_name and not contact_no and not address:
                    break
                choir_list.append({
                    'name': name,
                    'members': members,
                    'members_name': members_name,
                    'contact_no': contact_no,
                    'address': address
                })
                i += 1

        context = {
            'form1_data': form1_data,
            'form3_data': form3_data,
            'form2_data': form_data.form2_data,
            'form4_data': form4_display,
            'form5_data': form5_display,
            'number_range': number_range,
            'form6_data': form_data.form6_data,
            'form7_data': form7_data,
            'tanda_count': tanda_count,
            'development_works':development_works,
            'committee_members': committee_members,
            'temple_list':temple_list,
            'important_people': important_people,
            'choir_list': choir_list,
            'user': request.user,  # <-- Add this for template logic if needed
            
        }
        # Render the HTML template
        template = get_template('admin/submitted_form_download.html')
        html = template.render(context)

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Create an Excel workbook and worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Form Data"

        # Write data to Excel
        for table in soup.find_all('table'):
            headers = [th.text.strip() for th in table.find('thead').find_all('th')]
            ws.append(headers)
            for row in table.find('tbody').find_all('tr'):
                values = [td.text.strip() for td in row.find_all('td')]
                ws.append(values)

        # Prepare the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="form_{form_id}.xlsx"'
        wb.save(response)
        return response

    except FormData.DoesNotExist:
        return HttpResponse("Form not found.", status=404)

def submitted_form_download(request):
    submitted_data = FormData.objects.filter(is_completed=True).select_related('user')
    return render(request, 'admin/submitted_form_download.html', {'submitted_data': submitted_data})


from django.contrib.auth.decorators import login_required, user_passes_test

@login_required(login_url='admin_login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def edit_form(request, form_id):
    form_data = get_object_or_404(FormData, id=form_id)

    if request.method == 'POST':
        # --- Form 1 ---
        form1_data = form_data.form1_data or {}
        form1_data['taluka-name'] = request.POST.get('taluka-name', form1_data.get('taluka-name', ''))
        form1_data['gram-panchayat-name'] = request.POST.get('gram-panchayat-name', form1_data.get('gram-panchayat-name', ''))
        form1_data['village-name'] = request.POST.get('village-name', form1_data.get('village-name', ''))
        form1_data['zilla-parishad'] = request.POST.get('zilla-parishad', form1_data.get('zilla-parishad', ''))
        form1_data['num-approved-tandas'] = request.POST.get('num-approved-tandas', form1_data.get('num-approved-tandas', ''))
        form1_data['num-proposed-tandas'] = request.POST.get('num-proposed-tandas', form1_data.get('num-proposed-tandas', ''))
        # Handle tanda-wise info
        tanda_count = sum(1 for key in request.POST if key.startswith('tanda-name-'))
        for i in range(1, tanda_count + 1):
            form1_data[f'tanda-name-{i}'] = request.POST.get(f'tanda-name-{i}', form1_data.get(f'tanda-name-{i}', ''))
            form1_data[f'gram-panchayat-name-{i}'] = request.POST.get(f'gram-panchayat-name-{i}', form1_data.get(f'gram-panchayat-name-{i}', ''))
            form1_data[f'total-population-{i}'] = request.POST.get(f'total-population-{i}', form1_data.get(f'total-population-{i}', ''))
            form1_data[f'male-{i}'] = request.POST.get(f'male-{i}', form1_data.get(f'male-{i}', ''))
            form1_data[f'female-{i}'] = request.POST.get(f'female-{i}', form1_data.get(f'female-{i}', ''))
            form1_data[f'existing-facilities-{i}'] = request.POST.get(f'existing-facilities-{i}', form1_data.get(f'existing-facilities-{i}', ''))
            form1_data[f'electricity-available-{i}'] = request.POST.get(f'electricity-available-{i}', form1_data.get(f'electricity-available-{i}', ''))
            form1_data[f'water-facility-available-{i}'] = request.POST.get(f'water-facility-available-{i}', form1_data.get(f'water-facility-available-{i}', ''))
        form_data.form1_data = form1_data

        # --- Form 2 ---
        form2_data = form_data.form2_data or {}
        form2_data['tanda_name'] = request.POST.get('tanda_name', form2_data.get('tanda_name', ''))
        form2_data['taluka'] = request.POST.get('taluka', form2_data.get('taluka', ''))
        form2_data['district'] = request.POST.get('district', form2_data.get('district', ''))
        form2_data['female_population'] = request.POST.get('female_population', form2_data.get('female_population', ''))
        form2_data['male_population'] = request.POST.get('male_population', form2_data.get('male_population', ''))
        form2_data['total_population'] = request.POST.get('total_population', form2_data.get('total_population', ''))
        form2_data['gp_name'] = request.POST.get('gp_name', form2_data.get('gp_name', ''))
        form2_data['separate_gp_building'] = request.POST.get('separate_gp_building', form2_data.get('separate_gp_building', ''))
        form2_data['separate_tanda'] = request.POST.get('separate_tanda', form2_data.get('separate_tanda', ''))
        form2_data['gp_office_in_tanda'] = request.POST.get('gp_office_in_tanda', form2_data.get('gp_office_in_tanda', ''))
        form2_data['proposal_submitted'] = request.POST.get('proposal_submitted', form2_data.get('proposal_submitted', ''))
        form2_data['houses_sanctioned'] = request.POST.get('houses_sanctioned', form2_data.get('houses_sanctioned', ''))
        form2_data['houses_remaining'] = request.POST.get('houses_remaining', form2_data.get('houses_remaining', ''))
        form_data.form2_data = form2_data

        # --- Form 3 ---
        form3_data = []
        i = 1
        while True:
            name = request.POST.get(f'form3_name_{i}')
            designation = request.POST.get(f'form3_designation_{i}')
            contact = request.POST.get(f'form3_contact_{i}')
            if not name and not designation and not contact:
                break
            form3_data.append({
                'name': name,
                'designation': designation,
                'contact': contact
            })
            i += 1
        form_data.form3_data = form3_data

        # --- Form 4 ---
        form4_data = form_data.form4_data or {}
        form4_data['school_primary'] = request.POST.get('school_primary', form4_data.get('school_primary', ''))
        form4_data['school_secondary'] = request.POST.get('school_secondary', form4_data.get('school_secondary', ''))
        form4_data['college_distance'] = request.POST.get('college_distance', form4_data.get('college_distance', ''))
        form4_data['bus_stand'] = request.POST.get('bus_stand', form4_data.get('bus_stand', ''))
        form4_data['health_center'] = request.POST.get('health_center', form4_data.get('health_center', ''))
        form4_data['veterinary_disp'] = request.POST.get('veterinary_disp', form4_data.get('veterinary_disp', ''))
        form4_data['livestock_count'] = request.POST.get('livestock_count', form4_data.get('livestock_count', ''))
        form4_data['has_milk_center'] = request.POST.get('has_milk_center', form4_data.get('has_milk_center', ''))
        form4_data['milk_center_name'] = request.POST.get('milk_center_name', form4_data.get('milk_center_name', ''))
        form4_data['milk_center_number'] = request.POST.get('milk_center_number', form4_data.get('milk_center_number', ''))
        form4_data['cattle_details'] = request.POST.get('cattle_details', form4_data.get('cattle_details', ''))
        form4_data['shed_name'] = request.POST.get('shed_name', form4_data.get('shed_name', ''))
        form4_data['shed_number'] = request.POST.get('shed_number', form4_data.get('shed_number', ''))
        form4_data['electricity'] = request.POST.get('electricity', form4_data.get('electricity', ''))
        form4_data['ration_shop'] = request.POST.get('ration_shop', form4_data.get('ration_shop', ''))
        form4_data['ration_name'] = request.POST.get('ration_name', form4_data.get('ration_name', ''))
        form4_data['ration_number'] = request.POST.get('ration_number', form4_data.get('ration_number', ''))
        form4_data['water'] = request.POST.get('water', form4_data.get('water', ''))
        form4_data['water_name'] = request.POST.get('water_name', form4_data.get('water_name', ''))
        form4_data['water_number'] = request.POST.get('water_number', form4_data.get('water_number', ''))
        form4_data['fpo'] = request.POST.get('fpo', form4_data.get('fpo', ''))
        form4_data['fpo_name'] = request.POST.get('fpo_name', form4_data.get('fpo_name', ''))
        form4_data['fpo_number'] = request.POST.get('fpo_number', form4_data.get('fpo_number', ''))
        form4_data['hall'] = request.POST.get('hall', form4_data.get('hall', ''))
        form4_data['hall_name'] = request.POST.get('hall_name', form4_data.get('hall_name', ''))
        form4_data['hall_number'] = request.POST.get('hall_number', form4_data.get('hall_number', ''))
        form_data.form4_data = form4_data

        # --- Form 5 ---
        form5_data = []
        i = 1
        while True:
            name = request.POST.get(f'form5_name_{i}')
            position = request.POST.get(f'form5_position_{i}')
            contact = request.POST.get(f'form5_contact_{i}')
            if not name and not position and not contact:
                break
            form5_data.append({
                'name': name,
                'position': position,
                'contact': contact
            })
            i += 1
        form_data.form5_data = form5_data

        # --- Form 6 ---
        form6_data = form_data.form6_data or {}
        for j in range(1, 10):
            form6_data[f'work_{j}'] = request.POST.get(f'work_{j}', form6_data.get(f'work_{j}', ''))
        form6_data['needed_roads'] = request.POST.get('needed_roads', form6_data.get('needed_roads', ''))
        form6_data['proposed_works'] = request.POST.get('proposed_works', form6_data.get('proposed_works', ''))
        form_data.form6_data = form6_data

        # --- Form 7 ---
        form7_data = form_data.form7_data or {}

        # Location information
        form7_data['district_name'] = request.POST.get('district_name', form7_data.get('district_name', ''))
        form7_data['taluka'] = request.POST.get('taluka', form7_data.get('taluka', ''))
        form7_data['gram_panchayat_name'] = request.POST.get('gram_panchayat_name', form7_data.get('gram_panchayat_name', ''))
        form7_data['tanda_name'] = request.POST.get('tanda_name', form7_data.get('tanda_name', ''))

        # Population Details
        form7_data['number_of_women'] = request.POST.get('number_of_women', form7_data.get('number_of_women', ''))
        form7_data['number_of_men'] = request.POST.get('number_of_men', form7_data.get('number_of_men', ''))
        form7_data['number_of_children'] = request.POST.get('number_of_children', form7_data.get('number_of_children', ''))
        form7_data['number_of_little_girls'] = request.POST.get('number_of_little_girls', form7_data.get('number_of_little_girls', ''))
        form7_data['other'] = request.POST.get('other', form7_data.get('other', ''))
        form7_data['total_population'] = request.POST.get('total_population', form7_data.get('total_population', ''))

        # Gram Panchayat Infrastructure
        form7_data['separate_building'] = request.POST.get('separate_building', form7_data.get('separate_building', ''))
        form7_data['separate_place_name'] = request.POST.get('separate_place_name', form7_data.get('separate_place_name', ''))
        form7_data['public_private'] = request.POST.get('public_private', form7_data.get('public_private', ''))
        form7_data['place_area'] = request.POST.get('place_area', form7_data.get('place_area', ''))
        form7_data['proposal_submitted'] = request.POST.get('proposal_submitted', form7_data.get('proposal_submitted', ''))

        # Independent Gram Panchayat Status
        form7_data['separate_gp'] = request.POST.get('separate_gp', form7_data.get('separate_gp', ''))
        form7_data['revenue_status_eligibility'] = request.POST.get('revenue_status_eligibility', form7_data.get('revenue_status_eligibility', ''))
        form7_data['proposal_submitted_gp'] = request.POST.get('proposal_submitted_gp', form7_data.get('proposal_submitted_gp', ''))
        form7_data['resolution_date'] = request.POST.get('resolution_date', form7_data.get('resolution_date', ''))
        form7_data['submission_date'] = request.POST.get('submission_date', form7_data.get('submission_date', ''))
        form7_data['concerned_officer'] = request.POST.get('concerned_officer', form7_data.get('concerned_officer', ''))
        form7_data['pending'] = request.POST.get('pending', form7_data.get('pending', ''))

        # Housing plan information
        form7_data['total_houses'] = request.POST.get('total_houses', form7_data.get('total_houses', ''))
        form7_data['total_household_information'] = request.POST.get('total_household_information', form7_data.get('total_household_information', ''))
        form7_data['approved_houses'] = request.POST.get('approved_houses', form7_data.get('approved_houses', ''))
        form7_data['balance_houses'] = request.POST.get('balance_houses', form7_data.get('balance_houses', ''))


        # Facilities in Tanda
        form7_data['has_school'] = request.POST.get('has_school', form7_data.get('has_school', ''))
        form7_data['school_name'] = request.POST.get('school_name', form7_data.get('school_name', ''))
        form7_data['primary_secondary'] = request.POST.get('primary_secondary', form7_data.get('primary_secondary', ''))
        form7_data['school_village_name'] = request.POST.get('village_name', form7_data.get('school_village_name', ''))
        form7_data['school_distance'] = request.POST.get('school_distance', form7_data.get('school_distance', ''))
        form7_data['principals_name'] = request.POST.get('principals_name', form7_data.get('principals_name', ''))
        form7_data['school_contact_number'] = request.POST.get('contact_number', form7_data.get('school_contact_number', ''))

        # Milk Collection Center
        form7_data['has_milkcenter'] = request.POST.get('has_milkcenter', form7_data.get('has_milkcenter', ''))
        form7_data['center_name'] = request.POST.get('center_name', form7_data.get('center_name', ''))
        form7_data['owner_name'] = request.POST.get('owner_name', form7_data.get('owner_name', ''))
        form7_data['contact_number1'] = request.POST.get('contact_number1', form7_data.get('contact_number1', ''))
        form7_data['collection_capacity'] = request.POST.get('collection_capacity', form7_data.get('collection_capacity', ''))



        # Cow Shed
        form7_data['has_cowshed'] = request.POST.get('has_cowshed', form7_data.get('has_cowshed', ''))
        form7_data['gaushala_name'] = request.POST.get('gaushala_name', form7_data.get('gaushala_name', ''))
        form7_data['owner_name2'] = request.POST.get('owner_name2', form7_data.get('owner_name2', ''))
        form7_data['contact_number2'] = request.POST.get('contact_number2', form7_data.get('contact_number2', ''))
        form7_data['founding_year'] = request.POST.get('founding_year', form7_data.get('founding_year', ''))
        form7_data['number_of_livestock'] = request.POST.get('number_of_livestock', form7_data.get('number_of_livestock', ''))

        # Ration Shop
        form7_data['has_rationshop'] = request.POST.get('has_rationshop', form7_data.get('has_rationshop', ''))
        form7_data['shop_name'] = request.POST.get('shop_name', form7_data.get('shop_name', ''))
        form7_data['owner_name3'] = request.POST.get('owner_name3', form7_data.get('owner_name3', ''))
        form7_data['contact_number3'] = request.POST.get('contact_number3', form7_data.get('contact_number3', ''))
        form7_data['number_of_cardholder'] = request.POST.get('number_of_cardholder', form7_data.get('number_of_cardholder', ''))


  
        # --- Important People ---
        important_people = []
        i = 1
        while True:
            name = request.POST.get(f'important_person_name_{i}', '')
            designation = request.POST.get(f'important_person_designation_{i}', '')
            number = request.POST.get(f'important_person_number_{i}', '')
            if not any([name, designation, number]):
                break
            important_people.append({
                'name': name,
                'designation': designation,
                'number': number
            })
            i += 1
        form7_data['important_people'] = important_people

        # --- Committee Members ---
        committee_members = []
        i = 1
        while True:
            name = request.POST.get(f'committee_member_name_{i}', '')
            designation = request.POST.get(f'committee_member_designation_{i}', '')
            contact = request.POST.get(f'committee_member_contact_{i}', '')
            address = request.POST.get(f'committee_member_address_{i}', '')
            email = request.POST.get(f'committee_member_email_{i}', '')
            dob = request.POST.get(f'committee_member_dob_{i}', '')
            if not any([name, designation, contact, address, email, dob]):
                break
            committee_members.append({
                'name': name,
                'designation': designation,
                'contact': contact,
                'address': address,
                'email': email,
                'dob': dob
            })
            i += 1
        form7_data['committee_members'] = committee_members

        # --- Development Works ---
        development_works = []
        i = 1
        while True:
            name = request.POST.get(f'name_of_work_{i}', '')
            status = request.POST.get(f'status_{i}', '')
            nature = request.POST.get(f'nature_of_work_{i}', '')
            fund = request.POST.get(f'fund_provision_{i}', '')
            if not any([name, status, nature, fund]):
                break
            development_works.append({
                'name': name,
                'status': status,
                'nature': nature,
                'fund': fund
            })
            i += 1
        form7_data['development_works'] = development_works

        # --- Temples ---
        temple_list = []
        i = 1
        while True:
            name = request.POST.get(f'temple_name_{i}', '')
            place = request.POST.get(f'temple_place_{i}', '')
            location = request.POST.get(f'temple_location_{i}', '')
            area = request.POST.get(f'temple_area_{i}', '')
            proposal = request.POST.get(f'temple_proposal_{i}', '')
            funding = request.POST.get(f'temple_funding_{i}', '')
            if not any([name, place, location, area, proposal, funding]):
                break
            temple_list.append({
                'name': name,
                'place': place,
                'location': location,
                'area': area,
                'proposal': proposal,
                'funding': funding
            })
            i += 1
        form7_data['temple_list'] = temple_list

        # --- Choir (Bhajani Mandal) ---
        choir_list = []
        i = 1
        while True:
            name = request.POST.get(f'choir_name_{i}', '')
            members = request.POST.get(f'members_{i}', '')
            members_name = request.POST.get(f'members_name_{i}', '')
            contact_no = request.POST.get(f'contact_no_{i}', '')
            address = request.POST.get(f'address_{i}', '')
            if not any([name, members, members_name, contact_no, address]):
                break
            choir_list.append({
                'name': name,
                'members': members,
                'members_name': members_name,
                'contact_no': contact_no,
                'address': address
            })
            i += 1
        form7_data['choir_list'] = choir_list

        form_data.form7_data = form7_data



        form_data.save()
        return redirect('completed_works')

    # Build context similar to view_form_popup
    form1_data = form_data.form1_data or {}
    form4_data = form_data.form4_data or {}
    form5_data = form_data.form5_data or []
    form6_data = form_data.form6_data or {}
    form7_data = form_data.form7_data or {}
    number_range = range(1, 19)

    # --- Form 3 Display ---
    form3_data = []
    if isinstance(form_data.form3_data, list):
        form3_data = form_data.form3_data
    else:
        i = 1
        while True:
            name = form_data.form3_data.get(f'name_{i}')
            designation = form_data.form3_data.get(f'designation_{i}')
            contact = form_data.form3_data.get(f'contact_{i}')
            if not name and not designation and not contact:
                break
            form3_data.append({
                'name': name,
                'designation': designation,
                'contact': contact
            })
            i += 1

    # --- Form 5 Display ---
    form5_display = []
    if isinstance(form5_data, list):
        form5_display = form5_data
    else:
        i = 1
        while True:
            name = form5_data.get(f'name_{i}')
            position = form5_data.get(f'position_{i}')
            contact = form5_data.get(f'contact_{i}')
            if not name and not position and not contact:
                break
            form5_display.append({
                'name': name,
                'position': position,
                'contact': contact
            })
            i += 1

    form4_display = {
        'school_primary': form4_data.get('school_primary', ''),
        'school_secondary': form4_data.get('school_secondary', ''),
        'college_distance': form4_data.get('college_distance', ''),
        'bus_stand': form4_data.get('bus_stand', ''),
        'health_center': form4_data.get('health_center', ''),
        'veterinary_disp': form4_data.get('veterinary_disp', ''),
        'livestock_count': form4_data.get('livestock_count', ''),
        'has_milk_center': form4_data.get('has_milk_center', ''),
        'milk_center_name': form4_data.get('milk_center_name', ''),
        'milk_center_number': form4_data.get('milk_center_number', ''),
        'cattle_details': form4_data.get('cattle_details', ''),
        'shed_name': form4_data.get('shed_name', ''),
        'shed_number': form4_data.get('shed_number', ''),
        'electricity': form4_data.get('electricity', ''),
        'ration_shop': form4_data.get('ration_shop', ''),
        'ration_name': form4_data.get('ration_name', ''),
        'ration_number': form4_data.get('ration_number', ''),
        'water': form4_data.get('water', ''),
        'water_name': form4_data.get('water_name', ''),
        'water_number': form4_data.get('water_number', ''),
        'fpo': form4_data.get('fpo', ''),
        'fpo_name': form4_data.get('fpo_name', ''),
        'fpo_number': form4_data.get('fpo_number', ''),
        'hall': form4_data.get('hall', ''),
        'hall_name': form4_data.get('hall_name', ''),
        'hall_number': form4_data.get('hall_number', ''),
    }
    committee_members = []
    i = 1
    while True:
        name = form7_data.get(f'committee_member_name_{i}', '')
        designation = form7_data.get(f'committee_member_designation_{i}', '')
        contact = form7_data.get(f'committee_member_contact_{i}', '')
        address = form7_data.get(f'committee_member_address_{i}', '')
        email = form7_data.get(f'committee_member_email_{i}', '')
        dob = form7_data.get(f'committee_member_dob_{i}', '')
        if not any([name, designation, contact, address, email, dob]):
            break
        committee_members.append({
            'name': name,
            'designation': designation,
            'contact': contact,
            'address': address,
            'email': email,
            'dob': dob
        })
        i += 1
    form7_data['committee_members'] = committee_members



    # --- Form 3 Display (again, for context) ---
    tanda_count = sum(1 for key in form1_data if key.startswith('tanda-name-'))

    committee_members = form7_data.get('committee_members', [])
    development_works = form7_data.get('development_works', [])
    temple_list = form7_data.get('temple_list', [])
    important_people = form7_data.get('important_people', [])
    choir_list = form7_data.get('choir_list', [])

    context = {
        'form_data': form_data,
        'form1_data': form1_data,
        'form3_data': form3_data,
        'form2_data': form_data.form2_data,
        'form4_data': form4_display,
        'form5_data': form5_display,
        'number_range': number_range,
        'form6_data': form_data.form6_data,
        'form7_data': form7_data,
        'tanda_count': tanda_count,
        'user': request.user,
        'committee_members': committee_members,
        'development_works': development_works,
        'temple_list': temple_list, 
        'important_people': important_people,
        'choir_list': choir_list,
    }
    return render(request, 'admin/edit_form.html', context)

import openai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


openai.api_key = settings.OPENAI_API_KEY

import json
from difflib import get_close_matches

# Load the Q&A pairs from the JSON file
with open("static/json/qa.json", encoding="utf-8") as f:
    QA_PAIRS = json.load(f)

# Extract questions for easy searching
questions = [qa["question"] for qa in QA_PAIRS]

# Find the best match
def find_similar_answer(user_question, cutoff=0.6):
    matches = get_close_matches(user_question, questions, n=1, cutoff=cutoff)
    if matches:
        best_match = matches[0]
        # Find the corresponding answer
        for qa in QA_PAIRS:
            if qa["question"] == best_match:
                return qa["answer"]
    return None

system_prompt = (
    "You are a helpful assistant for a government CRM system used in Maharashtra. "
    "Always reply like you're speaking to a real person — be polite, use complete sentences, and avoid technical terms. "
    "Keep your answers short and clear, no more than 3 sentences. "
    "Always keep your replies within 100 tokens."
)


system_prompt = (
    "You are a helpful assistant for a government CRM system used in Maharashtra. "
    "Always reply like you're speaking to a real person — be polite, use complete sentences, and avoid technical terms. "
    "Keep your answers short and clear, no more than 3 sentences. "
    "Always keep your replies within 100 tokens."
)

@csrf_exempt
def get_bot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')

        # 1. Try finding an answer from embeddings
        similar_answer = find_similar_answer(message)
        if similar_answer:
            return JsonResponse({'response': similar_answer})

        # 2. Fall back to OpenAI GPT
        if 'conversation_history' not in request.session:
            request.session['conversation_history'] = [
                {"role": "system", "content": system_prompt}

            ]

        request.session['conversation_history'].append({"role": "user", "content": message})

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=request.session['conversation_history'],
                max_tokens=200,
                temperature=0.6,
                presence_penalty=0.3,
            )
            bot_response = response.choices[0].message.content.strip()
            request.session['conversation_history'].append({"role": "assistant", "content": bot_response})
            request.session.modified = True
        except Exception as e:
            bot_response = f"An error occurred: {e}"

        return JsonResponse({'response': bot_response})

    return JsonResponse({'error': 'Invalid request'}, status=400)
