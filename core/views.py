from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import FormView, RedirectView, TemplateView
from django.urls import reverse, reverse_lazy
from django.core.files.storage import FileSystemStorage
from .models import File, Owner
from .forms import FileForm, OwnerForm
import uuid
import os
import oci
from oci.object_storage import UploadManager
from oci.object_storage.models import CreateBucketDetails
from oci.object_storage.transfer.constants import MEBIBYTE


class HomeView(FormView):
    template_name = 'core/home.html'
    success_url = reverse_lazy('core:home')
    form_class = FileForm
    uploaded_file_url = None

    def get_context_data(self, **kwargs):
        ctx = {}
        if self.request.user.is_authenticated or self.request.session['user']:
            ctx['is_auth']: True
        return ctx

    def get_initial(self):
        owners = Owner.objects.all()
        return {'owner': owners}

    def form_valid(self, form):
        if not self.request.FILES:
            return self.form_invalid(form)
        if not self.request.user.is_authenticated:
            self.request.user, _ = Owner.objects.get_or_create(
                login_id=uuid.uuid1())  # make uuid based on host ID and current time
            self.request.user.is_authenticated = True
            self.request.user.save()
            self.request.session['user'] = self.request.user
        file = self.request.FILES['myfile']
        file_name = file.name
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        instance = form.save(commit=False)
        instance.file = file
        instance.name = file_name
        instance.owner = self.request.user
        instance.save()
        self.upload_cloud(uploaded_file_url)
        data = form.cleaned_json
        data.update({
            'file': file_name,
            'user_id': self.request.user.login_id,
        })
        return render(self.request, self.template_name, {'success': {
            'file': file_name,
            'user_id': self.request.user.login_id,
        }})

    def form_invalid(self, form):
        return super(HomeView, self).form_invalid(form)

    def upload_cloud(self, file):
        pass


class LoginView(FormView):
    template_name = 'core/login.html'
    success_url = reverse_lazy('core:user')
    form_class = OwnerForm

    def get_context_data(self, **kwargs):
        ctx = {}
        return ctx

    def form_valid(self, form):
        model = form.save(commit=False)
        return super(LoginView, self).form_valid(form)

    def form_invalid(self, form):
        return super(LoginView, self).form_invalid(form)


class UserView(TemplateView):
    template_name = 'core/user.html'

    def get_form_kwargs(self):
        pass

    def get_context_data(self, **kwargs):
        self.get_files()
        ctx = {}
        return ctx

    def get_files(self):
        pass
