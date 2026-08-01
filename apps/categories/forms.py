from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name', 'slug', 'description', 'icon', 'color', 
            'parent', 'order', 'is_active', 'is_featured', 'image'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].widget.attrs['readonly'] = True
        self.fields['parent'].queryset = Category.objects.filter(is_active=True)
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            qs = Category.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A category with this slug already exists.")
        return slug
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            qs = Category.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A category with this name already exists.")
        return name