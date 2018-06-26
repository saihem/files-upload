from django import forms
from .models import File, Owner
from .mixins import JsonFormMixin


class FileForm(JsonFormMixin, forms.ModelForm):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False)
    name = forms.CharField(required=False)

    class Meta:
        model = File
        fields = 'name', 'file',


class OwnerForm(forms.ModelForm):
    login_id = forms.CharField()

    class Meta:
        model = Owner
        fields = 'login_id',
