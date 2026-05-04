from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm
from bookings.models import Booking
from cars.models import Car, Favorite
from django.db.models import Sum, Count

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == 'admin':
            return reverse_lazy('admin_dashboard')
        elif user.role == 'staff':
            return reverse_lazy('staff_dashboard')
        return reverse_lazy('dashboard')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        import json
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == 'admin':
            # In our system 'completed' or 'active' usually represent revenue, let's use completed, active, and confirmed.
            # But the existing code used 'approved' which might have been a typo from earlier or an old status.
            # I'll update it to check for 'completed', 'active', 'confirmed' which are valid.
            revenue_statuses = ['completed', 'active', 'confirmed']
            context['total_revenue'] = Booking.objects.filter(status__in=revenue_statuses).aggregate(Sum('total_price'))['total_price__sum'] or 0
            context['total_bookings'] = Booking.objects.count()
            context['total_cars'] = Car.objects.count()
            context['total_favorites'] = Favorite.objects.count()
            context['recent_bookings'] = Booking.objects.all().order_by('-created_at')[:5]
            
            # Analytics Data
            # 1. Bookings by Status
            status_counts = Booking.objects.values('status').annotate(count=Count('id'))
            context['status_labels'] = json.dumps([item['status'].upper() for item in status_counts])
            context['status_data'] = json.dumps([item['count'] for item in status_counts])
            
            # 2. Revenue by Brand
            brand_revenue = Booking.objects.filter(status__in=revenue_statuses).values('car__brand').annotate(total=Sum('total_price'))
            context['brand_labels'] = json.dumps([item['car__brand'].upper() for item in brand_revenue])
            context['brand_data'] = json.dumps([float(item['total']) if item['total'] else 0 for item in brand_revenue])
            
        elif user.role == 'staff':
            context['pending_bookings'] = Booking.objects.filter(status='pending').count()
            context['active_rentals'] = Booking.objects.filter(status='active').count()
            context['recent_requests'] = Booking.objects.filter(status='pending').order_by('-created_at')[:10]
        else:
            context['my_bookings'] = Booking.objects.filter(user=user).order_by('-created_at')
        return context
