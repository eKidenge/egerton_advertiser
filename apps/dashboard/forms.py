from django import forms
from .models import DashboardWidget, DashboardPreference

class DashboardWidgetForm(forms.ModelForm):
    class Meta:
        model = DashboardWidget
        fields = ['widget_type', 'title', 'column', 'width', 'settings']
        widgets = {
            'settings': forms.Textarea(attrs={'rows': 3, 'placeholder': 'JSON settings...'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['widget_type'].widget.attrs['class'] = 'form-select'
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['column'].widget.attrs['class'] = 'form-control'
        self.fields['width'].widget.attrs['class'] = 'form-control'
        self.fields['settings'].widget.attrs['class'] = 'form-control'

class DashboardPreferenceForm(forms.ModelForm):
    class Meta:
        model = DashboardPreference
        fields = ['theme', 'default_view', 'refresh_interval', 'notifications_enabled']
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'default_view': forms.Select(attrs={'class': 'form-select'}),
            'refresh_interval': forms.NumberInput(attrs={'class': 'form-control'}),
        }