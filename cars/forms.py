from django import forms
from .models import Car, MaintenanceLog

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Professional placeholders for choice fields
        placeholder_map = {
            'car_type': 'Select Vehicle Type',
            'fuel_type': 'Select Fuel Type',
            'transmission': 'Select Transmission',
            'status': 'Set Initial Status'
        }
        
        for field_name, label in placeholder_map.items():
            if field_name in self.fields:
                choices = list(self.fields[field_name].choices)
                # If the first choice is the default "---------", replace it.
                # Otherwise, just prepend our professional label.
                if choices and choices[0][0] == '':
                    choices[0] = ('', label)
                else:
                    choices.insert(0, ('', label))
                self.fields[field_name].choices = choices

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class MaintenanceLogForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        fields = ['car', 'log_type', 'description', 'mileage_at_service', 'cost']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Professional placeholders for foreign keys and choices
        self.fields['car'].empty_label = "Select Vehicle"
        self.fields['log_type'].choices = [('', 'Select Log Category')] + list(self.fields['log_type'].choices)[1:]
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
