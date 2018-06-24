from django.views.generic import FormView, RedirectView, TemplateView
from django.urls import reverse, reverse_lazy
from .models import File, Owner
import os
import oci
from oci.object_storage import UploadManager
from oci.object_storage.models import CreateBucketDetails
from oci.object_storage.transfer.constants import MEBIBYTE


class HomeView(FormView):
    template_name = 'core/home.html'
    success_url = reverse_lazy('core:home')

    def post(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        pass

    def form_valid(self, form):
        pass

    def form_invalid(self, form):
        pass


class LoginView(FormView):
    template_name = 'core/login.html'
    success_url = reverse_lazy('core:home')

    def post(self, request, *args, **kwargs):
        pass

    def get_context_data(self, **kwargs):
        pass

    def form_valid(self, form):
        pass

    def form_invalid(self, form):
        pass
