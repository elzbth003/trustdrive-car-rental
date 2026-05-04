from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from bookings.models import Booking
from .models import Payment
from django.contrib import messages

class PaymentCreateView(LoginRequiredMixin, View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        return render(request, 'payments/payment_form.html', {'booking': booking})

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        method = request.POST.get('method')
        
        # Payment simulation: succeed automatically
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            method=method,
            status='completed',
            transaction_id='TXN' + str(booking.id) + 'SIM'
        )
        
        messages.success(request, "Payment successful! Your booking is pending approval.")
        return redirect('booking_list')
