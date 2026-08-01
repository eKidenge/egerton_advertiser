from django import forms
from django.utils import timezone
from .models import Advertisement, Category, Article

class AdvertisementForm(forms.ModelForm):
    targeted_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    targeted_articles = forms.ModelMultipleChoiceField(
        queryset=Article.objects.filter(status='published'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    target_countries = forms.CharField(required=False, help_text="Comma-separated country names")
    target_cities = forms.CharField(required=False, help_text="Comma-separated city names")
    
    class Meta:
        model = Advertisement
        fields = [
            'title', 'description', 'image', 'image_alt', 'video_url',
            'link_url', 'link_target', 'position', 'size',
            'company_name', 'contact_email', 'contact_phone',
            'start_date', 'end_date', 'status',
            'targeted_categories', 'targeted_articles', 'target_countries', 'target_cities',
            'budget', 'cost_per_click', 'cost_per_impression',
            'max_clicks', 'max_impressions', 'daily_limit', 'priority'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        if start_date and start_date < timezone.now():
            raise forms.ValidationError("Start date cannot be in the past.")
        
        return cleaned_data
    
    def clean_target_countries(self):
        value = self.cleaned_data.get('target_countries', '')
        if value:
            return [c.strip() for c in value.split(',') if c.strip()]
        return []
    
    def clean_target_cities(self):
        value = self.cleaned_data.get('target_cities', '')
        if value:
            return [c.strip() for c in value.split(',') if c.strip()]
        return []

class AdvertisementFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Advertisement.STATUS_CHOICES),
        required=False
    )
    position = forms.ChoiceField(
        choices=[('', 'All Positions')] + list(Advertisement.POSITION_CHOICES),
        required=False
    )
    advertiser = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="All Advertisers"
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))