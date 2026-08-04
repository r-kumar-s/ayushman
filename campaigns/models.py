from django.db import models

# Create your models here.

class Consultation(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    age = models.PositiveIntegerField(null=True, blank=True)
    condition = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)