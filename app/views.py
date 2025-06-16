from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.utils.http import urlencode
from django.shortcuts import redirect

from .models import *
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
        return redirect('app:book_session')
    
    # Retrieve selected services from session
    service_ids = request.session.get('selected_services', [])
    if not service_ids:
        messages.error(request, "No services selected.")
        return redirect('app:services')
    
    # Store booking data in session
    request.session['booking_data'] = form_data
    request.session.modified = True
    
    # Redirect to payment page
    return redirect('app:payment')

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
        return redirect('app:services')
    
    context = {
        'booking_data': booking_data,
        'selected_services': selected_services,
    }
    return render(request, 'payment.html', context)

@require_POST
def payment_confirm_view(request):
    """
    Process Monnify payment confirmation.
    """
    transaction_ref = request.POST.get('transactionRef')
    payment_ref = request.POST.get('paymentRef')
    
    if not transaction_ref or not payment_ref:
        messages.error(request, "Invalid payment details.")
        return redirect('app:payment')
    
    # Placeholder: Verify payment with Monnify API
    # In production, use Monnify's API to verify transaction_ref
    print(f"Payment Confirmation: TransactionRef={transaction_ref}, PaymentRef={payment_ref}")
    
    # Retrieve booking data
    booking_data = request.session.get('booking_data', {})
    service_ids = request.session.get('selected_services', [])
    selected_services = [SERVICES.get(sid, "Unknown Service") for sid in service_ids if sid in SERVICES]
    
    # Placeholder: Save booking to database
    booking = Booking.objects.create(
        full_name=booking_data.get('fullName', ''),
        email=booking_data.get('email', ''),
        phone_number=booking_data.get('phoneNumber', ''),
        institution=booking_data.get('institution', ''),
        academic_level=booking_data.get('academicLevel', ''),
        department=booking_data.get('department', ''),
        programme=booking_data.get('programme', ''),
        research_area=booking_data.get('researchArea', ''),
        contact_method=booking_data.get('contactMethod', ''),
        transaction_ref=transaction_ref,
    )

    booking.set_services(selected_services)
    booking.save()

    print(f"Confirmed Booking: {booking_data}, Services={selected_services}, TransactionRef={transaction_ref}")
    
    # Clear session data
    request.session.pop('booking_data', None)
    request.session.pop('selected_services', None)
    request.session.modified = True
    
    # # Redirect to success page
    # return redirect('app:payment_success', name=booking_data.get('fullName', ''),
    #                 contact=booking_data.get('email', ''), transaction=transaction_ref)

    # build URL with query parameters
    base_url = reverse('app:payment_success')
    query_string = urlencode({
        'name': booking_data.get('fullName', ''),
        'contact': booking_data.get('email', ''),
        'transaction': transaction_ref
    })
    url = f'{base_url}?{query_string}'
    return redirect(url)


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
    return render(request, 'payment-success.html', context)

def about_view(request):
    return render(request, 'about.html')

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
    return render(request, 'contact.html', context)

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
    return redirect('app:contact')

def how_it_works_view(request):
    return render(request, 'core/how_it_works.html')

def testimonials_view(request):
    return render(request, 'core/testimonials.html')

def faq_view(request):
    return render(request, 'core/faq.html')

def finalize_payment_view(request):
    """
    Render the finalize payment page post-consultation.
    """
    step = request.GET.get('step', '1')
    try:
        step = int(step)
        if step not in [1, 2, 3, 4]:
            print('gotheee')
            step = 1
    except ValueError:
        step = 1

    
    total_amount = request.GET.get('amount', '0')
    
    # Assume consultation_data is set post-consultation
    # consultation_data = request.session.get('consultation_data', {})
    # service_ids = request.session.get('selected_services', [])  # Reusing selected_services
    # selected_services = [
    #     {'id': sid, 'title': SERVICES.get(sid, {}).get('title', "Unknown Service"), 'price': SERVICES.get(sid, {}).get('price', 0)}
    #     for sid in service_ids if sid in SERVICES
    # ]
    # total_amount = sum(service.get('price', 0) for service in selected_services)
    
    # if not consultation_data or not selected_services:
    #     messages.error(request, "No consultation data found. Please complete the consultation process.")
    #     return redirect('app:services')
    
    bank_details = {
        'bankName': "Stanbic bank",
        'accountName': "ResearchSupportDesk Limited",
        'accountNumber': "0007712778",
        'sortCode': "***",
    }
    
    context = {
        # 'consultation_data': consultation_data,
        # 'selected_services': selected_services,
        'total_amount': total_amount,
        'bank_details': bank_details,
        'current_step': step,
    }
    return render(request, 'finalize-payment.html', context)

def finalize_payment_review_view(request):
    return render(request, 'payment-success-review.html')

@require_POST
def finalize_payment_submit_view(request):
    """
    Process payment proof submission for final payment.
    """
    full_name = request.POST.get('fullName')
    email = request.POST.get('email')
    phone_number = request.POST.get('phoneNumber')
    institution = request.POST.get('institution')
    additional_notes = request.POST.get('additionalNotes')
    payment_proof = request.FILES.get('paymentProof')
    
    required_fields = ['fullName', 'email', 'phoneNumber', 'institution', 'paymentProof']
    missing_fields = [field for field in required_fields if not request.POST.get(field) and not request.FILES.get(field)]
    if missing_fields:
        messages.error(request, f"Please fill in all required fields: {', '.join(missing_fields)}.")
        return redirect('core:finalize_payment')
    
    if payment_proof:
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        max_size = 5 * 1024 * 1024  # 5MB
        if payment_proof.content_type not in allowed_types:
            messages.error(request, "Please upload a valid image (JPG, PNG) or PDF file.")
            return redirect('core:finalize_payment')
        if payment_proof.size > max_size:
            messages.error(request, "File size must be less than 5MB.")
            return redirect('core:finalize_payment')
        
        fs = FileSystemStorage(location='media/final_payment_proofs/')
        filename = fs.save(payment_proof.name, payment_proof)
        file_path = os.path.join('media/final_payment_proofs/', filename)
    
    # service_ids = request.session.get('selected_services', [])
    # selected_services = [
    #     {'id': sid, 'title': SERVICES.get(sid, {}).get('title', 'Unknown Service'), 'price': SERVICES.get(sid, {}).get('price', '0')}
    #     for sid in service_ids if sid in SERVICES
    # ]
    # total_amount = sum(service.get('price', 0) for service in selected_services)
    
    # Save to FinalPaymentSubmission model
    submission = FinalPaymentSubmission(
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        institution=institution,
        additional_notes=additional_notes,
        payment_proof=filename,
        total_amount=4000,
    )
    submission.save()
    
    # print(f"Final Payment Proof Submission: FullName={full_name}, Email={email}, Phone={phone_number}, "
    #       f"Institution={institution}, Notes={additional_notes}, File={file_path if payment_proof else 'None'}, "
    #       f"Services={selected_services}, Total=₦{total_amount}")
    
    request.session['final_payment_submitted'] = True
    request.session.modified = True
    return redirect('app:finalize_payment_review')

@require_POST
def consultation_complete_view(request):
    consultation_data = {
        'fullName': request.POST.get('fullName'),
        'email': request.POST.get('email'),
        'phoneNumber': request.POST.get('phoneNumber'),
        'institution': request.POST.get('institution'),
    }
    service_ids = request.POST.getlist('services')  # From consultation form
    try:
        service_ids = [int(sid) for sid in service_ids if int(sid) in SERVICES]
    except ValueError:
        messages.error(request, "Invalid service selection.")
        return redirect('core:services')
    
    request.session['consultation_data'] = consultation_data
    request.session['selected_services'] = service_ids
    request.session.modified = True
    return redirect('app:finalize_payment')