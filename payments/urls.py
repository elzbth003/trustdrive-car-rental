from django.urls import path
from .views import PaymentCreateView

urlpatterns = [
    path('process/<int:booking_id>/', PaymentCreateView.as_view(), name='payment_create'),
]
