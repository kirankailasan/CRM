"""
URL configuration for govt_crm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from crm import views, user_views, admin_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    path('get-user-details/<int:user_id>/', views.get_user_details, name='get_user_details'),
    path('all_forms', views.all_forms, name='all_forms'),
    #path('form<int:form_number>/', views.handle_form, name='handle_form'),
    path('save-form-data/', views.save_form_data, name='save_form_data'),
 
    path('completed_works/', views.completed_works, name='completed_works'),
    path('download-form/pdf/<int:form_id>/', views.download_form_pdf, name='download_form_pdf'),
    path('download-form/excel/<int:form_id>/', views.download_form_excel, name='download_form_excel'),
    path('edit_form/<int:form_id>/', views.edit_form, name='edit_form'),
    path('submitted-data/', views.view_submitted_data, name='submitted_data'),
    path('view-form-popup/<int:form_id>/', views.view_form_popup, name='view_form_popup'),
    path('submitted_form_download/', views.submitted_form_download, name ='submitted_form_download'),
    path('get_bot_response/', views.get_bot_response, name='get_bot_response'),


    path('appoint_user/', user_views.appoint_user, name='appoint_user'),
    path('faqs/', user_views.faqs, name='faqs'),
    path('tickets/', user_views.tickets, name='tickets'),
    
    
    path('manage_users/', admin_views.manage_users, name='manage_users'),
    path('create_user_view/', admin_views.create_user_view, name='create_user_view'),
    path('admin_tickets/', admin_views.admin_tickets, name='admin_tickets'),
    path('close_ticket/<int:ticket_id>/', admin_views.close_ticket, name='close_ticket'),
  





    path('', views.morph_effect, name='morph'),
    path('index', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path("check_all/", views.check_all, name="check_all"),
    path('scheme_detail', views.scheme_detail, name='scheme_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
