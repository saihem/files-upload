from django import forms
from .models import File, User


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('name', 'owner',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('login_id',)
