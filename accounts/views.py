import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Sum, Count

from .forms import CustomUserCreationForm, StaffCreationForm, AdminUserEditForm
from .models import User
from bookings.models import Booking
from cars.models import Car, Favorite

# Audit logger — logs important privilege operations
audit_log = logging.getLogger('rbac.audit')


# ─── Helper mixins ────────────────────────────────────────────────────────────

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allow only admin users."""
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.role == 'admin' or self.request.user.is_superuser
        )

    def handle_no_permission(self):
        messages.error(self.request, "Access denied. Admin privileges required.")
        return redirect('dashboard')


class StaffOrAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allow staff and admin users."""
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.role in ['admin', 'staff'] or
            self.request.user.is_superuser
        )

    def handle_no_permission(self):
        messages.error(self.request, "Access denied.")
        return redirect('dashboard')


# ─── Authentication ───────────────────────────────────────────────────────────

class RegisterView(CreateView):
    """
    Public registration — role is ALWAYS forced to 'customer' in the form's
    save() method. The role field is never shown to the user.
    """
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        # Redirect already-logged-in users
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully! Please log in.")
        return response


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'admin' or user.is_superuser:
            return reverse_lazy('admin_dashboard')
        elif user.role == 'staff':
            return reverse_lazy('staff_dashboard')
        return reverse_lazy('dashboard')


# ─── Role-specific dashboards ─────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, TemplateView):
    """Routes to correct dashboard based on role."""
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        import json
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == 'admin' or user.is_superuser:
            revenue_statuses = ['completed', 'active', 'confirmed']
            context['total_revenue'] = (
                Booking.objects.filter(status__in=revenue_statuses)
                .aggregate(Sum('total_price'))['total_price__sum'] or 0
            )
            context['total_bookings'] = Booking.objects.count()
            context['total_cars'] = Car.objects.count()
            context['total_favorites'] = Favorite.objects.count()
            context['total_staff'] = User.objects.filter(role='staff').count()
            context['total_customers'] = User.objects.filter(role='customer').count()
            context['recent_bookings'] = Booking.objects.select_related('car', 'user').order_by('-created_at')[:5]

            # Chart data
            status_counts = Booking.objects.values('status').annotate(count=Count('id'))
            context['status_labels'] = json.dumps([str(i['status']).upper() if i['status'] else "UNKNOWN" for i in status_counts])
            context['status_data'] = json.dumps([i['count'] for i in status_counts])

            brand_revenue = (
                Booking.objects.filter(status__in=revenue_statuses)
                .values('car__brand')
                .annotate(total=Sum('total_price'))
            )
            context['brand_labels'] = json.dumps([str(i['car__brand']).upper() if i['car__brand'] else "UNKNOWN" for i in brand_revenue])
            context['brand_data'] = json.dumps([float(i['total']) if i['total'] else 0 for i in brand_revenue])

            context['staff_list'] = User.objects.filter(role='staff').order_by('-date_joined')

        elif user.role == 'staff':
            context['pending_bookings'] = Booking.objects.filter(status='pending').count()
            context['active_rentals'] = Booking.objects.filter(status='active').count()
            context['recent_requests'] = (
                Booking.objects.filter(status='pending')
                .select_related('car', 'user')
                .order_by('-created_at')[:10]
            )

        else:
            # Customer
            context['my_bookings'] = (
                Booking.objects.filter(user=user)
                .select_related('car')
                .order_by('-created_at')
            )

        return context


class AdminDashboardView(AdminRequiredMixin, DashboardView):
    """Explicit admin dashboard URL — same view, access-guarded."""
    pass


class StaffDashboardRedirect(StaffOrAdminRequiredMixin, View):
    """Staff dashboard redirects to bookings staff view."""
    def get(self, request, *args, **kwargs):
        return redirect('staff_dashboard')


# ─── Admin: Staff Management ──────────────────────────────────────────────────

class StaffCreateView(AdminRequiredMixin, CreateView):
    """Admin creates a new staff account."""
    form_class = StaffCreationForm
    template_name = 'accounts/staff_create.html'
    success_url = reverse_lazy('admin_dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        new_staff = self.object
        audit_log.info(
            f"[RBAC] Admin '{self.request.user.username}' created staff "
            f"account '{new_staff.username}' (id={new_staff.id})"
        )
        messages.success(
            self.request,
            f"Staff account '{new_staff.username}' created successfully."
        )
        return response


class StaffToggleActiveView(AdminRequiredMixin, View):
    """Admin activates or deactivates a staff account."""
    def post(self, request, pk):
        staff = get_object_or_404(User, pk=pk, role='staff')
        staff.is_active = not staff.is_active
        staff.save()
        action = "activated" if staff.is_active else "deactivated"
        audit_log.info(
            f"[RBAC] Admin '{request.user.username}' {action} "
            f"staff '{staff.username}' (id={staff.id})"
        )
        messages.success(request, f"Staff '{staff.username}' has been {action}.")
        return redirect('admin_dashboard')


class StaffDeleteView(AdminRequiredMixin, View):
    """Admin removes a staff account (demotes to customer, preserves data)."""
    def post(self, request, pk):
        staff = get_object_or_404(User, pk=pk, role='staff')
        old_username = staff.username
        staff.role = 'customer'   # Demote rather than delete (preserves booking history)
        staff.save()
        audit_log.info(
            f"[RBAC] Admin '{request.user.username}' demoted "
            f"'{old_username}' (id={pk}) from staff to customer"
        )
        messages.warning(request, f"'{old_username}' has been removed from staff and demoted to customer.")
        return redirect('admin_dashboard')


class UserEditView(AdminRequiredMixin, View):
    """Admin edits any user's details (role, active status, contact info)."""
    def get(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        # Prevent editing other admins
        if target.role == 'admin' and not request.user.is_superuser:
            messages.error(request, "You cannot edit another admin's account.")
            return redirect('admin_dashboard')
        form = AdminUserEditForm(instance=target)
        return render(request, 'accounts/user_edit.html', {'form': form, 'target': target})

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target.role == 'admin' and not request.user.is_superuser:
            messages.error(request, "You cannot edit another admin's account.")
            return redirect('admin_dashboard')
        old_role = target.role
        form = AdminUserEditForm(request.POST, instance=target)
        if form.is_valid():
            updated = form.save()
            if updated.role != old_role:
                audit_log.info(
                    f"[RBAC] Admin '{request.user.username}' changed role of "
                    f"'{target.username}' from '{old_role}' to '{updated.role}'"
                )
            messages.success(request, f"User '{target.username}' updated successfully.")
            return redirect('admin_dashboard')
        return render(request, 'accounts/user_edit.html', {'form': form, 'target': target})
