import collections
import json
import oci

from oci.object_storage import UploadManager
from oci.object_storage.models import CreateBucketDetails
from oci.object_storage.transfer.constants import MEBIBYTE


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

    def set_config(self):
        config = oci.config.from_file()
        self.compartment_id = config["tenancy"]
        self.object_storage = oci.object_storage.ObjectStorageClient(config)
        self.namespace = self.object_storage.get_namespace().data

    def get_bucket(self):
        bucket_name = "Test_Bucket"
        print("Creating a new bucket {!r} in compartment {!r}".format(
            bucket_name, self.compartment_id))
        request = CreateBucketDetails()
        request.compartment_id = self.compartment_id
        request.name = bucket_name
        bucket = self.object_storage.create_bucket(self.namespace, request)
        request.compartment_id = self.compartment_id
        request.name = bucket_name
        return bucket_name

    def get_file(self, file_name, user):
        self.user = user
        self.set_config()
        bucket_name = self.get_bucket()
        object_name = "{}_{}".format(self.user, file_name)
        object = self.object_storage.get_object(
            self.namespace,
            bucket_name,
            object_name)
        return object

    def upload_cloud(self, file_properties, user=None):
        self.user = user
        file, file_name = file_properties
        self.set_config()
        bucket_name = self.get_bucket()
        object_name = "{}_{}".format(self.user, file_name)
        part_size = 2 * MEBIBYTE  # part size (in bytes)
        upload_manager = UploadManager(self.object_storage,
                                       allow_parallel_uploads=True,
                                       parallel_process_count=3)
        response = upload_manager.upload_file(
            self.namespace, bucket_name, object_name, file,
            part_size=part_size,
            progress_callback=self.progress_callback)
        return response

    @staticmethod
    def progress_callback(self, bytes_uploaded):
        print("{} additional bytes uploaded".format(bytes_uploaded))
