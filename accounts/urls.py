from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    RegisterView, UserLoginView, DashboardView,
    AdminDashboardView, StaffCreateView,
    StaffToggleActiveView, StaffDeleteView, UserEditView,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    UserLoginView.as_view(), name='login'),
    path('logout/',   LogoutView.as_view(next_page='login'), name='logout'),

    # ── Dashboards ────────────────────────────────────────
    path('dashboard/',       DashboardView.as_view(),      name='dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    # staff_dashboard is in bookings.urls (already exists there)

    # ── Admin: Staff Management ───────────────────────────
    path('staff/create/',               StaffCreateView.as_view(),       name='staff_create'),
    path('staff/<int:pk>/toggle/',      StaffToggleActiveView.as_view(), name='staff_toggle'),
    path('staff/<int:pk>/remove/',      StaffDeleteView.as_view(),       name='staff_remove'),
    path('users/<int:pk>/edit/',        UserEditView.as_view(),          name='user_edit'),
]
