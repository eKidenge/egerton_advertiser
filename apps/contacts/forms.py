from django import forms
from django.core.validators import EmailValidator
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Write your message here...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter your phone number (optional)'}),
            'subject': forms.TextInput(attrs={'placeholder': 'What is this about?'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message

class ContactReplyForm(forms.Form):
    response = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Type your response here...',
            'class': 'form-control'
        }),
        required=True
    )
    
    def clean_response(self):
        response = self.cleaned_data.get('response')
        if len(response.strip()) < 5:
            raise forms.ValidationError("Response must be at least 5 characters long.")
        return response

class ContactFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(ContactMessage.STATUS_CHOICES),
        required=False
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priority')] + list(ContactMessage.PRIORITY_CHOICES),
        required=False
    )
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))