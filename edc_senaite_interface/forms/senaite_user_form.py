from django import forms

from ..models import SenaiteUser


class SenaiteUserForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = SenaiteUser
        fields = '__all__'
