from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, F, Count
from django.contrib import messages
from .models import Car, MaintenanceLog, Review, Favorite
from .forms import CarForm, MaintenanceLogForm   # single consolidated import
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

class HomeView(TemplateView):
    template_name = 'cars/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_cars'] = Car.objects.filter(status='available')[:6]
        return context

class AboutView(TemplateView):
    template_name = 'cars/about.html'

class ServicesView(TemplateView):
    template_name = 'cars/services.html'

class ContactView(TemplateView):
    template_name = 'cars/contact.html'

class CarListView(ListView):
    model = Car
    template_name = 'cars/car_list.html'
    context_object_name = 'cars'
    paginate_by = 9

    def get_queryset(self):
        queryset = Car.objects.filter(status='available')
        query = self.request.GET.get('q')
        car_type = self.request.GET.get('type')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(brand__icontains=query))
        if car_type:
            queryset = queryset.filter(car_type=car_type)
        if min_price:
            queryset = queryset.filter(daily_rate__gte=min_price)
        if max_price:
            queryset = queryset.filter(daily_rate__lte=max_price)
            
        return queryset

class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_favorites'] = Favorite.objects.filter(user=self.request.user).values_list('car_id', flat=True)
        else:
            context['user_favorites'] = []
        return context

# Admin/Staff Car management
class CarCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'
    success_url = reverse_lazy('car_list_admin')

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

class CarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'
    success_url = reverse_lazy('car_list_admin')

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

class CarDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = reverse_lazy('car_list_admin')

    def test_func(self):
        return self.request.user.role == 'admin'

class AdminCarListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Car
    template_name = 'cars/admin_car_list.html'
    context_object_name = 'cars'

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']
class MaintenanceListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = MaintenanceLog
    template_name = 'cars/maintenance_list.html'
    context_object_name = 'logs'

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

    def get_queryset(self):
        queryset = MaintenanceLog.objects.select_related('car', 'logged_by').order_by('-date')
        car_id = self.request.GET.get('car')
        if car_id:
            queryset = queryset.filter(car_id=car_id)
        return queryset

class MaintenanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MaintenanceLog
    form_class = MaintenanceLogForm
    template_name = 'cars/maintenance_form.html'
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_logs'] = MaintenanceLog.objects.select_related('car').order_by('-date')[:5]
        context['total_maintenance_cost'] = sum(log.cost for log in MaintenanceLog.objects.all())
        return context

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

    def form_valid(self, form):
        form.instance.logged_by = self.request.user
        return super().form_valid(form)

@login_required
def add_review(request, car_id):
    if request.method == 'POST':
        car = get_object_or_404(Car, id=car_id)
        # Prevent duplicate reviews from the same user
        if Review.objects.filter(car=car, user=request.user).exists():
            messages.warning(request, "You have already reviewed this vehicle.")
            return redirect('car_detail', pk=car_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if not rating or not comment:
            messages.error(request, "Please provide both a rating and a comment.")
            return redirect('car_detail', pk=car_id)
        Review.objects.create(
            car=car,
            user=request.user,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, "Your review has been submitted.")
        return redirect('car_detail', pk=car_id)
    return redirect('car_detail', pk=car_id)

@login_required
def toggle_favorite(request, car_id):
    if request.user.role != 'customer':
        return redirect('car_detail', pk=car_id)
        
    car = get_object_or_404(Car, id=car_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, car=car)
    
    if not created:
        favorite.delete()
        
    return redirect('car_detail', pk=car_id)

class FleetAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Car
    template_name = 'cars/fleet_analytics.html'
    context_object_name = 'cars'

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

    def get_queryset(self):
        return Car.objects.annotate(
            fav_count=Count('favorited_by'),
            rev_count=Count('reviews')
        ).order_by('-fav_count')
