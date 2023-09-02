from .models import Comment
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='', min_length=3, max_length=1000,
        widget=forms.Textarea(
            attrs={'placeholder': 'Leave a Comment :)', 'rows':3}
        )
    )
    class Meta:
        model = Comment
        fields = ('content',)
