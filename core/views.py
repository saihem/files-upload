import uuid
import datetime
import os
import pytz

from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.conf import settings
from django.http.response import HttpResponse, Http404

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
            ctx['is_auth'] = True
            ctx['user'] = self.request.session.get('user', None)
            ctx['file_name'] = self.request.session.get('file_name', None)
        return ctx

    def form_valid(self, form):
        if not self.request.FILES:
            return self.form_invalid(form)
        if not self.request.user.is_authenticated:
            try:
                login_id = self.request.session['user']
                self.request.user = Owner.objects.get(
                    login_id=login_id)
            except (KeyError, Owner.DoesNotExist):
                self.request.user = Owner.objects.create(
                    login_id=uuid.uuid1())  # make uuid based on host ID and current time
                self.request.user.is_authenticated = True
                self.request.user.save()
                self.request.session['user'] = str(self.request.user.login_id)
        instance = form.save(commit=False)
        file = instance.file
        instance.name = file.name
        instance.owner = self.request.user
        instance.save()
        self.request.session['file_name'] = file.name
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
        return super(HomeView, self).form_valid(form)

    def form_invalid(self, form):
        return super(HomeView, self).form_invalid(form)


class LoginView(FormView):
    template_name = 'core/login.html'
    success_url = reverse_lazy('core:user')
    form_class = OwnerForm

    def form_valid(self, form):
        instance = form.save()
        self.request.session['user'] = str(instance.login_id)
        return super(LoginView, self).form_valid(form)


class UserView(OracleMixin, TemplateView):
    template_name = 'core/user.html'

    def get_context_data(self, **kwargs):
        ctx = super(UserView, self).get_context_data(**kwargs)
        user = Owner.objects.get(login_id=self.request.session['user'])
        ctx['files'] = self.get_files(user)
        ctx['user_id'] = user.id
        return ctx

    def get_files(self, user):
        files = []
        for file in File.objects.filter(
                owner=user).select_related('owner'):
            file_object = self.get_object(
                user=user.login_id,
                file_name=file.file.name)
            files.append({'name': file.name,
                          'path_file_name': file.file.name,
                          'upload': file.updated_at.replace(
                              tzinfo=datetime.timezone.utc).astimezone(
                              tz=pytz.timezone('US/Eastern')).strftime(
                              '%Y-%m-%d %I:%M:%S %p'),
                          'download': file_object})
        return files


def download_file(request, path, pk):
    try:
        File.objects.get(owner_id=pk)
    except File.DoesNotExist:
        raise Http404
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(),
                                content_type="application/vnd.ms-excel")
        response[
            'Content-Disposition'] = 'inline; filename=' + os.path.basename(
            file_path)
        return response
