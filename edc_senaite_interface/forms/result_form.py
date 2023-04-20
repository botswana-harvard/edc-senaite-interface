from django import forms

from ..models import SenaiteResult


class SenaiteResultForm(forms.ModelForm):

    class Meta:
        model = SenaiteResult
        fields = '__all__'
