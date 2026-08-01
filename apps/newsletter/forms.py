from django import forms
from django.utils import timezone
from django.core.validators import EmailValidator
from .models import Subscriber, Newsletter
from apps.articles.models import Article
from apps.categories.models import Category
from apps.tags.models import Tag


class SubscriberForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Subscriber
        fields = ['email', 'name', 'categories', 'tags', 'frequency']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values if editing
        if self.instance and self.instance.pk:
            self.fields['categories'].initial = self.instance.categories.all()
            self.fields['tags'].initial = self.instance.tags.all()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            # Check if already exists (case insensitive)
            if Subscriber.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("This email is already subscribed.")
        return email


class NewsletterForm(forms.ModelForm):
    articles = forms.ModelMultipleChoiceField(
        queryset=Article.objects.filter(status='published'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    target_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Newsletter
        fields = [
            'subject', 'preview_text', 'content', 'template',
            'articles', 'target_categories', 'status', 'scheduled_for'
        ]
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter newsletter subject'}),
            'preview_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preview text shown in email clients'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'template': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values if editing
        if self.instance and self.instance.pk:
            self.fields['articles'].initial = self.instance.articles.all()
            self.fields['target_categories'].initial = self.instance.target_categories.all()
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        scheduled_for = cleaned_data.get('scheduled_for')
        
        if status == 'scheduled' and not scheduled_for:
            raise forms.ValidationError("Please set a scheduled date/time.")
        
        if scheduled_for and scheduled_for < timezone.now():
            raise forms.ValidationError("Scheduled date cannot be in the past.")
        
        return cleaned_data


class NewsletterFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Newsletter.STATUS_CHOICES),
        required=False,
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