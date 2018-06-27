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
    '''
    Gets Configuration creds
    create bucket
    gets object with user and file_name
    '''
    compartment_id = None
    namespace = None
    object_storage = None
    user = None
    bucket_name = 'files_app'

    def set_config(self):
        config = oci.config.from_file()
        self.compartment_id = config["tenancy"]
        self.object_storage = oci.object_storage.ObjectStorageClient(config)
        self.namespace = self.object_storage.get_namespace().data

    def create_bucket(self, new_bucket):
        self.set_config()
        request = CreateBucketDetails()
        request.compartment_id = self.compartment_id
        request.name = new_bucket
        bucket = self.object_storage.create_bucket(self.namespace, request)
        return bucket.data

    def get_object(self, file_name, user):
        self.user = user
        self.set_config()
        object_name = "{}_{}".format(self.user, file_name)
        try:
            object = self.object_storage.get_object(
                self.namespace,
                self.bucket_name,
                object_name)
            retrieved_file = 'FROM-ORACLE-' + file_name
            retrieved_file_path = self.get_media_file_path(retrieved_file)
            self.write_to_file(object, retrieved_file_path)
        except Exception as e:
            object = None
            retrieved_file = None
        return retrieved_file

    def upload_object(self, file_properties, user=None):
        self.user = user
        file, file_name = file_properties
        self.set_config()
        object_name = "{}_{}".format(self.user, file_name)
        part_size = 2 * MEBIBYTE  # part size (in bytes)
        upload_manager = UploadManager(self.object_storage,
                                       allow_parallel_uploads=True,
                                       parallel_process_count=3)
        file_path = self.get_media_file_path(file)
        response = upload_manager.upload_file(
            self.namespace, self.bucket_name, object_name,
            file_path,
            part_size=part_size,
            progress_callback=self.progress_callback)
        if response.status == 200:
            os.remove(file_path)
        return response

    @staticmethod
    def progress_callback(bytes_uploaded):
        if not bytes_uploaded:
            bytes_uploaded = 0
        print("{} additional bytes uploaded".format(bytes_uploaded))

    @staticmethod
    def get_media_file_path(file):
        media_os = os.path.join(os.path.abspath(os.path.dirname(__name__)),
                                settings.MEDIA_ROOT)
        return os.path.join(media_os, os.path.basename(file))

    @staticmethod
    def write_to_file(object, file_name):
        with open(file_name, 'wb') as f:
            for chunk in object.data.raw.stream(1024 * 1024,
                                                decode_content=False):
                f.write(chunk)
