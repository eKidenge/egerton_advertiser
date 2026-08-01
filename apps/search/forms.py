from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search news, articles, topics...',
            'class': 'form-control'
        })
    )
    type = forms.ChoiceField(
        choices=[
            ('all', 'All'),
            ('articles', 'Articles'),
            ('categories', 'Categories'),
            ('tags', 'Tags'),
            ('authors', 'Authors')
        ],
        required=False,
        initial='all'
    )

class AdvancedSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter keywords...',
            'class': 'form-control'
        })
    )
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    author = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tags separated by commas'}))
    sort_by = forms.ChoiceField(
        choices=[
            ('newest', 'Newest First'),
            ('oldest', 'Oldest First'),
            ('popular', 'Most Popular'),
            ('relevance', 'Relevance')
        ],
        required=False,
        initial='newest'
    )