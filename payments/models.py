from django.db import models

# Create your models here.
class Order(models.Model):
  user_id = models.IntegerField()
  customer_details = models.TextField()
  order_id = models.CharField(max_length=255, blank=False)
  order_amount = models.CharField(max_length=15)
  order_quantity = models.IntegerField()
  order_currency = models.CharField(max_length=15,default='INR')
  order_address = models.TextField()
  order_note = models.TextField()
  order_meta = models.TextField()
  order_response = models.TextField()
  order_status = models.CharField(max_length=255,default='STARTED')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = "orders"