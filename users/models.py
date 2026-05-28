from django.db import models
from django.utils.timezone import now

class User(models.Model):
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255, blank=True, null=True)

    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True, blank=True, null=True)

    address = models.TextField()

    dob = models.DateField(null=True, blank=True)  # ✅ fixed
    referred_by = models.CharField(max_length=255, blank=True, null=True)

    start_date = models.DateField(auto_now_add=True)  # ✅ fixed

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fname} {self.lname or ''} ({self.email})"

    class Meta:
        db_table = "users"
        ordering = ['-created_at']


class PatientFollowup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followups')

    diagnosis = models.CharField(max_length=255)
    treatments = models.TextField()

    prescription_file = models.FileField(upload_to='prescriptions/', null=True, blank=True)
    invoice_file = models.FileField(upload_to='invoices/', null=True, blank=True)

    followup_date = models.DateField(default=now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Followup - {self.user.fname} ({self.followup_date})"

    class Meta:
        db_table = "patient_followups"
        ordering = ['-created_at']