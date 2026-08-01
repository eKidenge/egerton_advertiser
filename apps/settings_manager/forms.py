from django import forms
from .models import SiteSetting, ThemeSetting

class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = ['category', 'key', 'value', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ThemeSettingForm(forms.ModelForm):
    class Meta:
        model = ThemeSetting
        fields = [
            'primary_color', 'secondary_color', 'success_color',
            'danger_color', 'warning_color', 'info_color',
            'light_color', 'dark_color',
            'font_family', 'font_size',
            'layout', 'sidebar_position',
            'custom_css', 'custom_js'
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'success_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'danger_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'warning_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'info_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'light_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'dark_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'font_family': forms.Select(attrs={'class': 'form-select'}),
            'font_size': forms.Select(attrs={'class': 'form-select'}),
            'layout': forms.Select(attrs={'class': 'form-select'}),
            'sidebar_position': forms.Select(attrs={'class': 'form-select'}),
            'custom_css': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': '/* Add your custom CSS here */'}),
            'custom_js': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '// Add your custom JavaScript here'}),
        }

class GeneralSettingsForm(forms.Form):
    site_name = forms.CharField(max_length=100, required=True)
    site_tagline = forms.CharField(max_length=200, required=False)
    site_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    site_logo = forms.ImageField(required=False)
    site_favicon = forms.ImageField(required=False)
    site_timezone = forms.ChoiceField(
        choices=[
            ('UTC', 'UTC'),
            ('Africa/Nairobi', 'Africa/Nairobi (EAT)'),
            ('Africa/Cairo', 'Africa/Cairo'),
            ('Africa/Johannesburg', 'Africa/Johannesburg'),
            ('Europe/London', 'Europe/London'),
            ('America/New_York', 'America/New_York'),
        ],
        required=True
    )
    site_language = forms.ChoiceField(
        choices=[
            ('en', 'English'),
            ('sw', 'Swahili'),
            ('fr', 'French'),
            ('es', 'Spanish'),
        ],
        required=True
    )

class EmailSettingsForm(forms.Form):
    smtp_host = forms.CharField(max_length=200, required=True)
    smtp_port = forms.IntegerField(required=True, initial=587)
    smtp_username = forms.CharField(max_length=200, required=True)
    smtp_password = forms.CharField(widget=forms.PasswordInput, required=False)
    use_tls = forms.BooleanField(required=False, initial=True)
    from_email = forms.EmailField(required=True)
    from_name = forms.CharField(max_length=200, required=True)

class SEOSettingsForm(forms.Form):
    meta_title = forms.CharField(max_length=70, required=True)
    meta_description = forms.CharField(max_length=160, widget=forms.Textarea(attrs={'rows': 2}), required=True)
    meta_keywords = forms.CharField(max_length=200, required=False)
    google_analytics_id = forms.CharField(max_length=50, required=False)
    google_verification = forms.CharField(max_length=100, required=False)
    bing_verification = forms.CharField(max_length=100, required=False)
    robots_txt = forms.CharField(widget=forms.Textarea(attrs={'rows': 6}), required=False)
    enable_sitemap = forms.BooleanField(required=False, initial=True)