from django.db import models
import json

# Create your models here.
class Booking(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    institution = models.CharField(max_length=255)
    academic_level = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    programme = models.CharField(max_length=100)
    research_area = models.CharField(max_length=255)
    contact_method = models.CharField(max_length=50)
    services = models.TextField()  # Store JSON as string
    created_at = models.DateTimeField(auto_now_add=True)

    def set_services(self, services_data):
        """Serialize services data to JSON string."""
        self.services = json.dumps(services_data)

    def get_services(self):
        """Deserialize JSON string to Python object."""
        return json.loads(self.services) if self.services else []

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

class ContactInquiry(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class FinalPaymentSubmission(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    institution = models.CharField(max_length=255)
    additional_notes = models.TextField(blank=True)
    payment_proof = models.FileField(upload_to='final_payment_proofs/')
    services = models.TextField()  # Store JSON as string
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_services(self, services_data):
        """Serialize services data to JSON string."""
        self.services = json.dumps(services_data)

    def get_services(self):
        """Deserialize JSON string to Python object."""
        return json.loads(self.services) if self.services else []

    class Meta:
        verbose_name = "Final Payment Submission"
        verbose_name_plural = "Final Payment Submissions"