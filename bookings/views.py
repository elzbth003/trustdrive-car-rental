from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Booking
from cars.models import Car
from django.db.models import F
from .forms import BookingForm
from django.urls import reverse_lazy

class BookingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'

    def test_func(self):
        # Only customers can book cars
        return self.request.user.role == 'customer'

    def form_valid(self, form):
        car = get_object_or_404(Car, pk=self.kwargs['car_id'])
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        # Double booking check
        overlapping_bookings = Booking.objects.filter(
            car=car,
            status__in=['pending', 'confirmed', 'active'],
            start_date__lt=end_date,
            end_date__gt=start_date
        )

        if overlapping_bookings.exists():
            form.add_error(None, "This car is already booked for the selected dates.")
            return self.form_invalid(form)

        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.car = car
        duration = (end_date - start_date).days
        if duration <= 0: duration = 1
        booking.total_price = car.daily_rate * duration
        booking.save()
        
        # Redirect to payment simulation
        return redirect('payment_create', booking_id=booking.id)

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        if self.request.user.role in ['admin', 'staff']:
            return Booking.objects.all().order_by('-created_at')
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

class StaffDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'bookings/staff_dashboard.html'
    context_object_name = 'bookings'

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

    def get_queryset(self):
        # In a real app, we would filter by staff.branch == booking.car.branch
        # For now, show all for the assigned role
        queryset = Booking.objects.select_related('car', 'user').order_by('-created_at')
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = Booking.objects.filter(status='pending').count()
        context['active_count'] = Booking.objects.filter(status='active').count()
        # Find cars where current_km >= last_service_km + 5000
        context['overdue_cars'] = Car.objects.filter(current_km__gte=F('last_service_km') + 5000)
        return context

class StaffBookingActionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    fields = [] # We'll handle logic in post
    
    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        action = request.POST.get('action')
        
        if action == 'confirm':
            booking.status = 'confirmed'
            messages.success(request, f"Booking {booking.id} confirmed.")
        elif action == 'checkout':
            booking.status = 'active'
            messages.success(request, f"Vehicle checked out for Booking {booking.id}.")
        elif action == 'return':
            booking.status = 'completed'
            # Update mileage
            new_km = request.POST.get('current_km')
            if new_km:
                booking.car.current_km = int(new_km)
                booking.car.save()
            messages.success(request, f"Vehicle returned for Booking {booking.id}.")
        elif action == 'cancel':
            booking.status = 'cancelled'
            messages.warning(request, f"Booking {booking.id} cancelled.")
        
        booking.save()
        return redirect('staff_dashboard')
