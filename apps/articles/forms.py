# apps/articles/forms.py

from django import forms
from django.utils import timezone
from django.forms import inlineformset_factory
from .models import Article, Category, Tag, ArticleImage
from django.contrib.auth import get_user_model

User = get_user_model()


class ArticleImageForm(forms.ModelForm):
    """Form for individual article images with caption and byline"""
    
    class Meta:
        model = ArticleImage
        fields = ['image', 'caption', 'byline', 'is_featured', 'order', 'alt_text']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter photo caption (e.g., "Sunset over Nairobi skyline")'
            }),
            'byline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Photo by [Photographer Name] or [Source]'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the image for accessibility (SEO)'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': 0,
                'placeholder': 'Display order (0 = first)'
            }),
        }
        labels = {
            'image': '📷 Upload Image',
            'caption': '📝 Caption',
            'byline': '✍️ Byline / Credit',
            'is_featured': '⭐ Featured Image',
            'order': '🔢 Display Order',
            'alt_text': '📌 Alt Text (SEO)',
        }
        help_texts = {
            'caption': 'Describe what is happening in the photo',
            'byline': 'Credit the photographer or image source (e.g., "Photo by John Doe")',
            'alt_text': 'Essential for accessibility and SEO - describe the image in detail',
            'is_featured': 'Mark this as the main image for the article',
            'order': 'Lower numbers appear first in the gallery',
        }
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be under 10MB.")
            
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
            if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    "Invalid image format. Please use JPG, PNG, GIF, WEBP, or SVG."
                )
        return image


# Create the inline formset for managing multiple images
ArticleImageFormSet = inlineformset_factory(
    Article,
    ArticleImage,
    form=ArticleImageForm,
    extra=5,  # Show 5 empty forms for uploading images
    max_num=20,  # Maximum 20 images per article
    can_delete=True,  # Allow deleting images
    can_order=False,  # We'll use our own order field
)


class ArticleForm(forms.ModelForm):
    # Simple textarea for content - no CKEditor
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control textarea-content',
            'rows': 20,
            'placeholder': 'Write your article content here...',
            'style': 'font-family: Times New Roman, serif; font-size: 16px; line-height: 1.8;'
        }),
        required=True,
        help_text="Write your article content. You can use HTML tags: <b>, <i>, <ul>, <li>, etc."
    )
    tags = forms.CharField(
        required=False, 
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    publish_option = forms.ChoiceField(
        choices=Article.PUBLISH_OPTIONS,
        required=False,
        initial=Article.PUBLISH_NOW,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    scheduled_for = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'excerpt', 'content', 'featured_image',
            'featured_image_alt', 'featured_image_caption', 'category',
            'status', 'is_featured', 'is_breaking', 'is_exclusive',
            'is_editor_pick', 'scheduled_for'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a compelling title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'A short summary of your article'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'featured_image_alt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Describe the image for accessibility'}),
            'featured_image_caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Caption for the image'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_breaking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_exclusive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_editor_pick': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'featured_image': 'Upload a main image for the article. You can also add more images with captions below.',
            'featured_image_alt': 'Describe the featured image for screen readers and SEO',
            'featured_image_caption': 'A caption for the featured image shown below the image',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        
        # Set category choices
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['category'].empty_label = "Select a category"
        
        # Set initial tags if editing
        if self.instance and self.instance.pk:
            tags = self.instance.tags.all()
            self.fields['tags'].initial = ', '.join([tag.name for tag in tags])
    
    def clean_tags(self):
        tag_string = self.cleaned_data.get('tags', '')
        if tag_string:
            tag_names = [t.strip() for t in tag_string.split(',') if t.strip()]
            return tag_names
        return []
    
    def clean_scheduled_for(self):
        scheduled_for = self.cleaned_data.get('scheduled_for')
        if scheduled_for and scheduled_for < timezone.now():
            raise forms.ValidationError("Scheduled date cannot be in the past.")
        return scheduled_for
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            # Check if slug is unique
            qs = Article.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("An article with this slug already exists.")
        return slug
    
    def save(self, commit=True):
        article = super().save(commit=False)
        
        if commit:
            article.save()
            # Handle tags
            tag_names = self.cleaned_data.get('tags', [])
            if tag_names:
                tags = []
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    tags.append(tag)
                article.tags.set(tags)
            else:
                article.tags.clear()
        
        return article


class ArticleFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Article.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    author = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="All Authors",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )