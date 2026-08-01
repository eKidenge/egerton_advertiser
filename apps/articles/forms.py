from django import forms
from django.utils import timezone
from ckeditor.widgets import CKEditorWidget
from .models import Article, Category, Tag
from django.contrib.auth import get_user_model

User = get_user_model()


class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    tags = forms.CharField(required=False, help_text="Enter tags separated by commas")
    publish_option = forms.ChoiceField(
        choices=Article.PUBLISH_OPTIONS,
        required=False,
        initial=Article.PUBLISH_NOW
    )
    scheduled_for = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'excerpt', 'content', 'featured_image',
            'featured_image_alt', 'featured_image_caption', 'category',
            'status', 'is_featured', 'is_breaking', 'is_exclusive',
            'is_editor_pick', 'scheduled_for'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].widget.attrs['readonly'] = True
        
        # Set category choices
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        
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
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories"
    )
    author = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="All Authors"
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search...'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )