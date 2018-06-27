import uuid
import json

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import FileForm, OwnerForm
from .models import Owner, File
from .mixins import OracleMixin


class HomeView(OracleMixin, FormView):
    template_name = 'core/home.html'
    success_url = reverse_lazy('core:home')
    form_class = FileForm
    uploaded_file_url = None

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated or 'user' in self.request.session:
            ctx['is_auth']: True
        return ctx

    def form_valid(self, form):
        if not self.request.FILES:
            return self.form_invalid(form)
        if not self.request.user.is_authenticated:
            try:
                user = self.request.session['user'].login_id
                self.request.user = Owner.objects.get(
                    login_id=user)
            except (KeyError, Owner.DoesNotExist):
                self.request.user = Owner.objects.create(
                    login_id=uuid.uuid1())  # make uuid based on host ID and current time
                self.request.user.is_authenticated = True
                self.request.user.save()
                self.request.session['user'] = self.request.user
        instance = form.save(commit=False)
        file = instance.file
        instance.name = file.name
        instance.owner = self.request.user
        instance.save()
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        response = self.upload_object(
            file_properties=(uploaded_file_url, file.name),
            user=self.request.user.login_id)
        data = form.cleaned_json
        data.update({'success': {
            'response': response.status,
            'file': file.name,
            'user_id': str(self.request.user.login_id),
        }})
        return render(self.request, self.template_name, data)
        # return HttpResponse(json.simplejson.dumps(data),
        #                     mimetype="application/json")

    def form_invalid(self, form):
        return super(HomeView, self).form_invalid(form)


class LoginView(FormView):
    template_name = 'core/login.html'
    success_url = reverse_lazy('core:user')
    form_class = OwnerForm

    def form_valid(self, form):
        instance = form.save()
        if not 'user' in self.request.session:
            self.request.session['user'] = instance
        return super(LoginView, self).form_valid(form)


class UserView(OracleMixin, TemplateView):
    template_name = 'core/user.html'

    def get_context_data(self, **kwargs):
        ctx = super(UserView, self).get_context_data(**kwargs)
        ctx['files'] = self.get_files()
        return ctx

    def get_files(self):
        files = []
        for file in File.objects.filter(
                user=self.request.session['user']).select_related(
            'owner'):
            file_object = self.get_object(
                user=str(self.request.session['user'].login_id),
                file_name=file.name)
            files.append({'name': file.name,
                          'upload': file.updated_at,
                          'download': file_object})
        return files
