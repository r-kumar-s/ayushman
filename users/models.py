from django.db import models

# Create your models here.

class User(models.Model):
  fname = models.CharField(max_length=255, blank=False)
  lname = models.CharField(max_length=255)
  phone = models.CharField(max_length=15, blank=False)
  email = models.CharField(max_length=255)  
  address = models.TextField(blank=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = "users"