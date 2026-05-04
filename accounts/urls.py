from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import RegisterView, UserLoginView, DashboardView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin-dashboard/', DashboardView.as_view(), name='admin_dashboard'),
    path('staff-dashboard/', DashboardView.as_view(), name='staff_dashboard'),
]
