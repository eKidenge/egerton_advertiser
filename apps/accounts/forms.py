# apps/accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import User, UserActivityLog, UserProfile
import re

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='subscriber',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    newsletter_subscription = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms and conditions.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to default fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        
        # Add help text for password
        self.fields['password1'].help_text = (
            'Password must be at least 8 characters long and contain at least '
            'one uppercase letter, one lowercase letter, one number, and one special character.'
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                raise ValidationError('A user with this username already exists.')
            if not re.match(r'^[\w.@+-]+$', username):
                raise ValidationError('Username contains invalid characters. Use only letters, numbers, and @/./+/-/_ .')
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        
        if password1 and len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        if password1 and not re.search(r'[A-Z]', password1):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        if password1 and not re.search(r'[a-z]', password1):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        if password1 and not re.search(r'\d', password1):
            raise ValidationError('Password must contain at least one number.')
        
        if password1 and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError('Password must contain at least one special character.')
        
        return password2
    
    def clean_terms(self):
        terms = self.cleaned_data.get('terms')
        if not terms:
            raise ValidationError('You must agree to the terms and conditions.')
        return terms


class UserLoginForm(AuthenticationForm):
    """Form for user login"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your country'})
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'})
    )
    organization = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your organization'})
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'bio',
                 'profile_picture', 'website', 'social_links')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourwebsite.com'}),
            'social_links': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'JSON format: {"twitter": "url", "facebook": "url"}'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate profile fields from related profile
        if self.instance and hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['date_of_birth'].initial = profile.date_of_birth
            self.fields['gender'].initial = profile.gender
            self.fields['country'].initial = profile.country
            self.fields['city'].initial = profile.city
            self.fields['organization'].initial = profile.organization
        
        # Make email read-only
        self.fields['email'].widget.attrs['readonly'] = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_social_links(self):
        social_links = self.cleaned_data.get('social_links')
        if social_links:
            try:
                import json
                json.loads(social_links)
            except json.JSONDecodeError:
                raise ValidationError('Social links must be valid JSON format.')
        return social_links
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            # Update or create profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            profile.gender = self.cleaned_data.get('gender')
            profile.country = self.cleaned_data.get('country')
            profile.city = self.cleaned_data.get('city')
            profile.organization = self.cleaned_data.get('organization')
            profile.save()
        
        return user


class UserCreateForm(forms.ModelForm):
    """Form for admin to create users"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        required=True
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='subscriber',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    send_welcome_email = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role',
                 'department', 'phone_number', 'profile_picture', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add department choices if available
        if hasattr(User, 'DEPARTMENT_CHOICES'):
            self.fields['department'].choices = [('', 'Select Department')] + list(User.DEPARTMENT_CHOICES)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        
        if password and len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            # Create profile if it doesn't exist
            UserProfile.objects.get_or_create(user=user)
        
        return user


class UserEditForm(forms.ModelForm):
    """Form for admin to edit users"""
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password (optional)'})
    )
    confirm_new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role',
                 'department', 'phone_number', 'profile_picture',
                 'is_active', 'is_verified', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add department choices if available
        if hasattr(User, 'DEPARTMENT_CHOICES'):
            self.fields['department'].choices = [('', 'Select Department')] + list(User.DEPARTMENT_CHOICES)
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        
        if new_password or confirm_new_password:
            if new_password != confirm_new_password:
                raise ValidationError('New passwords do not match.')
            
            if len(new_password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Update password if provided
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
        
        return user


class PasswordResetForm(forms.Form):
    """Form for password reset request"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if not User.objects.filter(email=email).exists():
                raise ValidationError('No user found with this email address.')
        return email


class UserActivityFilterForm(forms.Form):
    """Form for filtering user activity logs"""
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="All Users",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    action = forms.ChoiceField(
        choices=[('', 'All Actions')] + list(UserActivityLog.ACTION_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('Start date must be before or equal to end date.')
        
        return cleaned_data


class UserBulkActionForm(forms.Form):
    """Form for bulk actions on users"""
    action = forms.ChoiceField(
        choices=[
            ('', 'Select Action'),
            ('activate', 'Activate Users'),
            ('deactivate', 'Deactivate Users'),
            ('verify', 'Verify Users'),
            ('unverify', 'Unverify Users'),
            ('delete', 'Delete Users'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    user_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def clean_user_ids(self):
        user_ids = self.cleaned_data.get('user_ids')
        if user_ids:
            try:
                ids = [int(id) for id in user_ids.split(',') if id]
                return ids
            except ValueError:
                raise ValidationError('Invalid user IDs.')
        return []


class UserExportForm(forms.Form):
    """Form for exporting user data"""
    format = forms.ChoiceField(
        choices=[
            ('csv', 'CSV'),
            ('excel', 'Excel'),
            ('pdf', 'PDF'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fields = forms.MultipleChoiceField(
        choices=[
            ('id', 'ID'),
            ('username', 'Username'),
            ('email', 'Email'),
            ('first_name', 'First Name'),
            ('last_name', 'Last Name'),
            ('role', 'Role'),
            ('department', 'Department'),
            ('phone_number', 'Phone Number'),
            ('is_active', 'Active'),
            ('is_verified', 'Verified'),
            ('date_joined', 'Date Joined'),
            ('last_login', 'Last Login'),
        ],
        initial=['username', 'email', 'first_name', 'last_name', 'role'],
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    role_filter = forms.ChoiceField(
        choices=[('', 'All Roles')] + list(User.ROLE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status_filter = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('verified', 'Verified'),
            ('unverified', 'Unverified'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )