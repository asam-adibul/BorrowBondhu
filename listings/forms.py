from django import forms
from .models import Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'category', 'price_per_day', 'location', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }