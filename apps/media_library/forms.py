from django import forms
from .models import MediaFile, MediaTag, MediaCategory

class MediaFileForm(forms.ModelForm):
    tag_names = forms.CharField(required=False, help_text="Enter tags separated by commas")
    category_id = forms.ModelChoiceField(
        queryset=MediaCategory.objects.all(),
        required=False,
        empty_label="Select Category"
    )
    
    class Meta:
        model = MediaFile
        fields = ['file', 'title', 'description', 'alt_text']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (10MB max)
            if file.size > 10485760:
                raise forms.ValidationError("File size cannot exceed 10MB.")
            
            # Check file extension
            valid_extensions = [
                '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
                '.mp4', '.webm', '.ogg', '.mp3', '.wav',
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
            ]
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(f"Unsupported file type. Allowed: {', '.join(valid_extensions)}")
        
        return file
    
    def clean_tag_names(self):
        value = self.cleaned_data.get('tag_names', '')
        if value:
            return [t.strip() for t in value.split(',') if t.strip()]
        return []

class MediaFilterForm(forms.Form):
    file_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(MediaFile.MEDIA_TYPES),
        required=False
    )
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    tag = forms.ModelChoiceField(queryset=MediaTag.objects.all(), required=False, empty_label="All Tags")

class MediaTagForm(forms.ModelForm):
    class Meta:
        model = MediaTag
        fields = ['name', 'slug']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].widget.attrs['readonly'] = True

class MediaCategoryForm(forms.ModelForm):
    class Meta:
        model = MediaCategory
        fields = ['name', 'slug', 'description', 'parent']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].widget.attrs['readonly'] = True
        self.fields['parent'].queryset = MediaCategory.objects.all()