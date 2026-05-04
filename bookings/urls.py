from django.urls import path
from .views import BookingCreateView, BookingListView, StaffDashboardView, StaffBookingActionView

urlpatterns = [
    path('create/<int:car_id>/', BookingCreateView.as_view(), name='booking_create'),
    path('my-bookings/', BookingListView.as_view(), name='booking_list'),
    path('staff/dashboard/', StaffDashboardView.as_view(), name='staff_dashboard'),
    path('staff/action/<int:pk>/', StaffBookingActionView.as_view(), name='staff_booking_action'),
]
