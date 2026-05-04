from django.urls import path
from .views import (
    CarListView, CarDetailView, CarCreateView, 
    CarUpdateView, CarDeleteView, AdminCarListView, AboutView, ServicesView, ContactView,
    MaintenanceListView, MaintenanceCreateView, add_review, toggle_favorite, FleetAnalyticsView
)

urlpatterns = [
    path('', CarListView.as_view(), name='car_list'),
    path('<int:pk>/', CarDetailView.as_view(), name='car_detail'),
    path('admin-list/', AdminCarListView.as_view(), name='car_list_admin'),
    path('analytics/', FleetAnalyticsView.as_view(), name='fleet_analytics'),
    path('add/', CarCreateView.as_view(), name='car_add'),
    path('<int:pk>/edit/', CarUpdateView.as_view(), name='car_edit'),
    path('<int:pk>/delete/', CarDeleteView.as_view(), name='car_delete'),
    path('about/', AboutView.as_view(), name='about'),
    path('services/', ServicesView.as_view(), name='services'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('maintenance/', MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenance/add/', MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('<int:car_id>/review/', add_review, name='add_review'),
    path('<int:car_id>/favorite/', toggle_favorite, name='toggle_favorite'),
]
