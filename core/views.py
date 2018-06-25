from django.views.generic import FormView, RedirectView, TemplateView
from django.urls import reverse, reverse_lazy
from .models import File, Owner
from .forms import FileForm, OwnerForm
import os
import oci
from oci.object_storage import UploadManager
from oci.object_storage.models import CreateBucketDetails
from oci.object_storage.transfer.constants import MEBIBYTE


class HomeView(FormView):
    template_name = 'core/home.html'
    success_url = reverse_lazy('core:home')
    form_class = FileForm

    def get_context_data(self, **kwargs):
        ctx = {}
        return ctx

    def get_initial(self):
        owners = Owner.objects.all()
        return {'owner': owners}

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('file_field')
        return self.form_valid()

    def form_valid(self, form):
        instance = form.save(commit=False)
        files = self.request.FILES
        return super(HomeView, self).form_valid(form)

    def form_invalid(self, form):
        if not form.data['owner'] or form.data['name']:
            self.form_valid()
        return super(HomeView, self).form_invalid(form)


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
        ctx = {}
        return ctx
