from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


# ─── Public Registration (role locked to 'customer') ─────────────────────────
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. A valid email address.")

    class Meta(UserCreationForm.Meta):
        model = User
        # 'role' intentionally excluded — backend forces 'customer'
        fields = ('username', 'email', 'phone_number')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'   # ALWAYS force customer — never trust frontend
        if commit:
            user.save()
        return user


# ─── Admin-only: Create Staff Account ────────────────────────────────────────
class StaffCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'staff'   # Admin-created accounts are always staff
        if commit:
            user.save()
        return user


# ─── Admin-only: Edit existing user ──────────────────────────────────────────
class AdminUserEditForm(UserChangeForm):
    password = None   # Don't expose password hash in admin edit

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'role', 'is_active')
        widgets = {
            'role': forms.Select(choices=User.ROLE_CHOICES),
        }

