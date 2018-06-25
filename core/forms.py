from django import forms
from .models import File, Owner


class FileForm(forms.ModelForm):
    file_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}))


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ('login_id',)
