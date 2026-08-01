from django import forms
from django.core.validators import EmailValidator
from .models import Subscriber, Newsletter

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email', 'name', 'categories', 'tags', 'frequency']
        widgets = {
            'categories': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
    
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
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
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
        required=False
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))