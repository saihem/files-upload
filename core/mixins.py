import collections
import json
import oci
import os

from django.conf import settings
from oci.object_storage import UploadManager
from oci.object_storage.models import CreateBucketDetails
from oci.object_storage.transfer.constants import MEBIBYTE

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class JsonFormMixin:
    cleaned_data = {}

    @property
    def cleaned_json(self):
        return {
            k: self.json_value(v)
            for k, v in self.cleaned_data.items()
        }

    def json_value(self, v):
        if not isinstance(v, str) and isinstance(v, collections.Iterable):
            cleaned_v = [self.json_value(i) for i in v]
        else:
            try:
                cleaned_v = json.dumps(v)
            except (TypeError, ValueError):
                cleaned_v = str(v)
        return cleaned_v


class OracleMixin:
    compartment_id = None
    namespace = None
    object_storage = None
    user = None
    bucket_name = 'Test_Bucket'

    def set_config(self):
        config = oci.config.from_file()
        self.compartment_id = config["tenancy"]
        self.object_storage = oci.object_storage.ObjectStorageClient(config)
        self.namespace = self.object_storage.get_namespace().data

    def create_bucket(self):
        request = CreateBucketDetails()
        request.compartment_id = self.compartment_id
        request.name = self.bucket_name
        bucket = self.object_storage.create_bucket(self.namespace, request)
        request.compartment_id = self.compartment_id
        request.name = self.bucket_name
        return self.bucket_name

    def get_file(self, file_name, user):
        self.user = user
        self.set_config()
        object_name = "{}_{}".format(self.user, file_name)
        object = self.object_storage.get_object(
            self.namespace,
            self.bucket_name,
            object_name)
        return object

    def upload_cloud(self, file_properties, user=None):
        self.user = user
        file, file_name = file_properties
        self.set_config()
        object_name = "{}_{}".format(self.user, file_name)
        part_size = 2 * MEBIBYTE  # part size (in bytes)
        upload_manager = UploadManager(self.object_storage,
                                       allow_parallel_uploads=True,
                                       parallel_process_count=3)
        file_path = self.get_file_path(file)
        response = upload_manager.upload_file(
            self.namespace, self.bucket_name, object_name,
            file_path,
            part_size=part_size,
            progress_callback=self.progress_callback)
        return response

    @staticmethod
    def progress_callback(bytes_uploaded):
        if not bytes_uploaded:
            bytes_uploaded = 0
        print("{} additional bytes uploaded".format(bytes_uploaded))

    def get_file_path(self, file):
        media_os = os.path.join(os.path.abspath(os.path.dirname(__name__)),
                                settings.MEDIA_ROOT)
        return os.path.join(media_os, os.path.basename(file))
