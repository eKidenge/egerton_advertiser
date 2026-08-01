from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

def validate_kenyan_phone(value):
    """Validate Kenyan phone numbers"""
    pattern = r'^(?:\+254|0)[17]\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Enter a valid Kenyan phone number (e.g., 0712345678 or +254712345678)'
        )

def validate_strong_password(value):
    """Validate password strength"""
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', value):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', value):
        raise ValidationError('Password must contain at least one number.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('Password must contain at least one special character.')

class CustomPasswordValidator:
    def validate(self, password, user=None):
        validate_strong_password(password)
    
    def get_help_text(self):
        return (
            "Your password must be at least 8 characters long, "
            "contain at least one uppercase letter, one lowercase letter, "
            "one number, and one special character."
        )