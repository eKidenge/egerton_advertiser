from django import forms
from .models import Tag

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'slug', 'description', 'color', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].widget.attrs['readonly'] = True
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            qs = Tag.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A tag with this slug already exists.")
        return slug
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            qs = Tag.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A tag with this name already exists.")
        return name