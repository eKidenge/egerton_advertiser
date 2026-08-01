from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Advertisement, AdvertisementView, AdvertisementClick
from apps.categories.models import Category
from apps.articles.models import Article

User = get_user_model()


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
    target_countries = forms.CharField(
        required=False,
        help_text="Comma-separated country names",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kenya, Uganda, Tanzania'})
    )
    target_cities = forms.CharField(
        required=False,
        help_text="Comma-separated city names",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nairobi, Mombasa, Kisumu'})
    )
    
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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ad title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your ad'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_alt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alt text for image'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/watch?v=...'}),
            'link_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourwebsite.com'}),
            'link_target': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@company.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254 700 000 000'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_per_click': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_per_impression': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_clicks': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'max_impressions': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'daily_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for targeted fields if editing
        if self.instance and self.instance.pk:
            self.fields['targeted_categories'].initial = self.instance.targeted_categories.all()
            self.fields['targeted_articles'].initial = self.instance.targeted_articles.all()
            
            # Convert JSON lists to comma-separated strings
            if self.instance.target_countries:
                self.fields['target_countries'].initial = ', '.join(self.instance.target_countries)
            if self.instance.target_cities:
                self.fields['target_cities'].initial = ', '.join(self.instance.target_cities)
    
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
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (5MB max)
            if image.size > 5242880:
                raise forms.ValidationError("Image file size cannot exceed 5MB.")
        return image
    
    def save(self, commit=True):
        ad = super().save(commit=False)
        
        if commit:
            ad.save()
            # Save many-to-many fields
            self.save_m2m()
            
            # Handle target countries and cities
            target_countries = self.cleaned_data.get('target_countries', [])
            target_cities = self.cleaned_data.get('target_cities', [])
            ad.target_countries = target_countries
            ad.target_cities = target_cities
            ad.save(update_fields=['target_countries', 'target_cities'])
        
        return ad


class AdvertisementFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Advertisement.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    position = forms.ChoiceField(
        choices=[('', 'All Positions')] + list(Advertisement.POSITION_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    advertiser = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="All Advertisers",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )