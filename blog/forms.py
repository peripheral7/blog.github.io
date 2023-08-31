from .models import Comment
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)