from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    aadhaar = models.CharField(max_length=14)
    address = models.TextField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class FormData(models.Model):

    form1_data = models.JSONField(default=dict, blank=True)
    form2_data = models.JSONField(default=dict, blank=True)
    form3_data = models.JSONField(default=dict, blank=True)
    form4_data = models.JSONField(default=dict, blank=True)
    form5_data = models.JSONField(default=dict, blank=True)
    form6_data = models.JSONField(default=dict, blank=True)
    form7_data = models.JSONField(default=dict, blank=True)

    # Optional: Additional fields like user, created_at, etc.
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='form_data')
    task = models.ForeignKey('TaskAssignment', on_delete=models.SET_NULL, null=True, blank=True, related_name='form_data')
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Form data for {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
    


class TaskAssignment(models.Model):
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignments")
    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    tanda = models.PositiveIntegerField(blank=True, null=True)
    deadline = models.DateField( blank=True, null=True)
    additional_instructions = models.TextField(blank=True, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.assigned_to.username} - {self.district} - {self.deadline}"
    

class TicketList(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    issue_type=models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description =models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=10, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"#{self.id} - {self.issue_type} - {self.title}"


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=255)
    status = models.CharField(max_length=10)
    date= models.DateTimeField(auto_now_add=True)
    verb = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.activity} - {self.status}"

