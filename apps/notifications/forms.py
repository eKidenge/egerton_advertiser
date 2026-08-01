from django import forms
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_comments', 'email_likes', 'email_mentions', 
            'email_article_published', 'email_subscriptions', 'email_digest',
            'push_comments', 'push_likes', 'push_mentions', 
            'push_article_published', 'push_ads',
            'in_app_comments', 'in_app_likes', 'in_app_mentions',
            'in_app_article_published', 'in_app_ads',
            'digest_frequency'
        ]
        widgets = {
            'digest_frequency': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add switch classes to checkbox inputs
        for field_name in self.fields:
            if isinstance(self.fields[field_name], forms.BooleanField):
                self.fields[field_name].widget.attrs['class'] = 'form-check-input'