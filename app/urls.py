from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import handler404
from django.shortcuts import render




# Define the custom 404 view
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

# Set the handler for 404 errors
handler404 = custom_404_view


app_name = "app"

urlpatterns = [
    path('services/', views.Services, name='services'),
    path('save-services/', views.save_services_view, name='save_services'),
    path('book-session/', views.book_session_view, name='book_session'),
    path('confirm-booking/', views.confirm_booking_view, name='confirm_booking'),
    path('payment/', views.payment_view, name='payment'),
    path('payment-confirm/', views.payment_confirm_view, name='payment_confirm'),
    path('payment-success/', views.payment_success_view, name='payment_success'),
    # Placeholder URLs for navigation
    path('', views.Index, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('contact-submit/', views.contact_submit_view, name='contact_submit'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    # path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    # path('testimonials/', views.testimonials_view, name='testimonials'),
    # path('faq/', views.faq_view, name='faq'),
] 


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, 
                          document_root=settings.MEDIA_ROOT)

# if settings.DEBUG is False:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)