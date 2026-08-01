from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your comment...',
                'class': 'form-control'
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 3:
            raise forms.ValidationError("Comment must be at least 3 characters long.")
        if len(content) > 2000:
            raise forms.ValidationError("Comment cannot exceed 2000 characters.")
        return content

class CommentModerationForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('spam', 'Mark as Spam')
        ],
        widget=forms.RadioSelect
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional moderation notes...'})
    )