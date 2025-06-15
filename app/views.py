from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os

# Create your views here.
# Create your views here.
def Index(request):
    return render(request, "index.html")

def About(request):
    return render(request, "aboutUs.html")

# Static service mapping (replace with Service model if needed)
SERVICES = {
    1: "Picking Thesis/Dissertation or Project Title",
    2: "Research Objective",
    3: "Methodology",
    4: "Literature Review",
    5: "Data Analysis",
    6: "Discussion of Findings",
    7: "Manuscript Production",
    8: "Assistance in Research Publication",
    9: "English Editing",
    10: "Plagiarism Check",
}

def Services(request):
    return render(request, "service.html")

@require_POST
def save_services_view(request):
    """
    Save selected services to session and redirect to booking page.
    """
    services = request.POST.getlist('services[]')
    if not services:
        messages.error(request, "Please select at least one service.")
        return redirect('services')
    
    # Convert service IDs to integers and validate
    try:
        service_ids = [int(sid) for sid in services if int(sid) in SERVICES]
    except ValueError:
        messages.error(request, "Invalid service selection.")
        return redirect('services')
    
    if not service_ids:
        messages.error(request, "No valid services selected.")
        return redirect('services')
    
    print('services', service_ids)

    # Save to session
    request.session['selected_services'] = service_ids
    request.session.modified = True  # Ensure session is saved
    
    return redirect('app:book_session')

def book_session_view(request):
    """
    Render the booking page with selected services from session.
    """
    service_ids = request.session.get('selected_services', [])
    # Map service IDs to titles
    selected_services = [
        {'id': sid, 'title': SERVICES.get(sid, "Unknown Service")}
        for sid in service_ids if sid in SERVICES
    ]
    
    context = {
        'selected_services': selected_services,
    }
    return render(request, 'book_session.html', context)

@require_POST
def confirm_booking_view(request):
    """
    Process booking form submission and redirect to payment.
    """
    # Retrieve form data
    form_data = {
        'fullName': request.POST.get('fullName'),
        'email': request.POST.get('email'),
        'phoneNumber': request.POST.get('phoneNumber'),
        'institution': request.POST.get('institution'),
        'academicLevel': request.POST.get('academicLevel'),
        'department': request.POST.get('department'),
        'programme': request.POST.get('programme'),
        'researchArea': request.POST.get('researchArea'),
        'contactMethod': request.POST.get('contactMethod'),
    }
    
    # Validate required fields
    required_fields = ['fullName', 'email', 'phoneNumber', 'institution', 'academicLevel', 'department', 'programme', 'researchArea', 'contactMethod']
    missing_fields = [field for field in required_fields if not form_data.get(field)]
    if missing_fields:
        messages.error(request, f"Please fill in all required fields: {', '.join(missing_fields)}.")
        return redirect('core:book_session')
    
    # Retrieve selected services from session
    service_ids = request.session.get('selected_services', [])
    if not service_ids:
        messages.error(request, "No services selected.")
        return redirect('core:services')
    
    # Store booking data in session
    request.session['booking_data'] = form_data
    request.session.modified = True
    
    # Redirect to payment page
    return redirect('core:payment')

def payment_view(request):
    """
    Render the payment page with booking data from session.
    """
    booking_data = request.session.get('booking_data', {})
    service_ids = request.session.get('selected_services', [])
    selected_services = [
        {'id': sid, 'title': SERVICES.get(sid, "Unknown Service")}
        for sid in service_ids if sid in SERVICES
    ]
    
    if not booking_data or not selected_services:
        messages.error(request, "No booking data found. Please complete the booking form.")
        return redirect('core:services')
    
    context = {
        'booking_data': booking_data,
        'selected_services': selected_services,
    }
    return render(request, 'core/payment.html', context)

@require_POST
def payment_confirm_view(request):
    """
    Process Monnify payment confirmation.
    """
    transaction_ref = request.POST.get('transactionRef')
    payment_ref = request.POST.get('paymentRef')
    
    if not transaction_ref or not payment_ref:
        messages.error(request, "Invalid payment details.")
        return redirect('core:payment')
    
    # Placeholder: Verify payment with Monnify API
    # In production, use Monnify's API to verify transaction_ref
    print(f"Payment Confirmation: TransactionRef={transaction_ref}, PaymentRef={payment_ref}")
    
    # Retrieve booking data
    booking_data = request.session.get('booking_data', {})
    service_ids = request.session.get('selected_services', [])
    selected_services = [SERVICES.get(sid, "Unknown Service") for sid in service_ids if sid in SERVICES]
    
    # Placeholder: Save booking to database
    print(f"Confirmed Booking: {booking_data}, Services={selected_services}, TransactionRef={transaction_ref}")
    
    # Clear session data
    request.session.pop('booking_data', None)
    request.session.pop('selected_services', None)
    request.session.modified = True
    
    # Redirect to success page
    return redirect('core:payment_success', name=booking_data.get('fullName', ''),
                    contact=booking_data.get('email', ''), transaction=transaction_ref)

def payment_success_view(request):
    """
    Render the payment success page.
    """
    name = request.GET.get('name', '')
    contact = request.GET.get('contact', '')
    transaction = request.GET.get('transaction', '')
    
    context = {
        'name': name,
        'contact': contact,
        'transaction': transaction,
    }
    return render(request, 'payment_success.html', context)

def about_view(request):
    return render(request, 'core/about.html')

def contact_view(request):
    """
    Render the contact page.
    """
    context = {
        'inquiry_types': [
            "General Inquiry", "Service Information", "Pricing Questions",
            "Technical Support", "Partnership Opportunities", "Complaint/Feedback", "Other"
        ],
        'office_hours': [
            {"day": "Monday - Friday", "hours": "9:00 AM - 6:00 PM"},
            {"day": "Saturday", "hours": "10:00 AM - 4:00 PM"},
            {"day": "Sunday", "hours": "Closed"}
        ]
    }
    return render(request, 'core/contact.html')

@require_POST
def contact_submit_view(request):
    """
    Process contact form submission.
    """
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    inquiry_type = request.POST.get('inquiryType')
    subject = request.POST.get('subject')
    message = request.POST.get('message')
    
    required_fields = ['name', 'email', 'inquiryType', 'subject', 'message']
    missing_fields = [field for field in required_fields if not request.POST.get(field)]
    if missing_fields:
        messages.error(request, f"Please fill in all required fields: {', '.join(missing_fields)}.")
        return redirect('core:contact')
    
    ContactInquiry.objects.create(name=name, email=email, phone=phone, inquiry_type=inquiry_type, subject=subject, message=message)
    # Placeholder: Log or send email
    print(f"Contact Form Submission: Name={name}, Email={email}, Phone={phone}, "
          f"InquiryType={inquiry_type}, Subject={subject}, Message={message}")
    
    # TODO: Implement email sending (e.g., with send_mail)
    # from django.core.mail import send_mail
    # send_mail(
    #     subject=f"Contact Form: {subject}",
    #     message=f"From: {name} ({email}, {phone})\nInquiry Type: {inquiry_type}\nMessage: {message}",
    #     from_email='info@researchsupportdesk.com',
    #     recipient_list=['admin@researchsupportdesk.com'],
    # )
    
    messages.success(request, "Thank you for your message! We'll get back to you within 24 hours.")
    return redirect('core:contact')

def how_it_works_view(request):
    return render(request, 'core/how_it_works.html')

def testimonials_view(request):
    return render(request, 'core/testimonials.html')

def faq_view(request):
    return render(request, 'core/faq.html')