from django.db import models

# Create your models here.
class Booking(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    institution = models.CharField(max_length=255)
    academic_level = models.CharField(max_length=10)
    department = models.CharField(max_length=255)
    programme = models.CharField(max_length=255)
    research_area = models.TextField()
    contact_method = models.CharField(max_length=50)
    services = models.JSONField()
    transaction_ref = models.CharField(max_length=100, unique=True)
    payment_ref = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class ContactInquiry(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)