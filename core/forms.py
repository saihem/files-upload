from django import forms
from .models import File, Owner
from .mixins import JsonFormMixin


class FileForm(JsonFormMixin, forms.ModelForm):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False)

    class Meta:
        model = File
        fields = 'file',


class OwnerForm(forms.ModelForm):
    login_id = forms.CharField()

    class Meta:
        model = Owner
        fields = 'login_id',

    def clean_login_id(self):
        login_id = self.cleaned_data.get('login_id')
        try:
            self.instance = Owner.objects.get(login_id=login_id)
        except Owner.DoesNotExist:
            pass
        return login_id

