from django import forms

class AnalyticsFilterForm(forms.Form):
    date_range = forms.ChoiceField(
        choices=[
            ('24h', 'Last 24 Hours'),
            ('7d', 'Last 7 Days'),
            ('30d', 'Last 30 Days'),
            ('90d', 'Last 90 Days'),
        ],
        required=False,
        initial='30d'
    )
    event_type = forms.ChoiceField(
        choices=[('', 'All Events')] + [
            ('page_view', 'Page View'),
            ('article_view', 'Article View'),
            ('click', 'Click'),
            ('scroll', 'Scroll'),
        ],
        required=False
    )
    device_type = forms.ChoiceField(
        choices=[('', 'All Devices'), ('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet')],
        required=False
    )