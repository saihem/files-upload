# import os
# from django.conf import settings
# user_ocid = os.environ["USER_OCID"]
# key_file = key_for(user_ocid)
#
# config = {
#     "user": user_ocid,
#     "key_file": key_file,
#     # "fingerprint": calc_fingerprint(key_file),
#     "tenancy": settings.tenancy,
#     "region": settings.region
# }
#
# from oci.config import validate_config
# validate_config(config)

from django.core.management import BaseCommand

import oci
from oci.identity import IdentityClient


class Command(BaseCommand):
    def handle(self, *args, **options):
        from oci.identity import IdentityClient
        config = oci.config.from_file()
        identity = IdentityClient(config)
        from oci.identity.models import CreateGroupDetails
        request = CreateGroupDetails()
        compartment_id = config["tenancy"]
        request.compartment_id = compartment_id
        request.name = "my-test-group"
        request.description = "Created with the Python SDK"
        group = identity.create_group(request)
        from oci.identity.models import CreateUserDetails
        request = CreateUserDetails()
        request.compartment_id = compartment_id
        request.name = "my-test-user"
        request.description = "Created with the Python SDK"
        user = identity.create_user(request)
        from oci.identity.models import AddUserToGroupDetails
        request = AddUserToGroupDetails()
        request.group_id = group.data.id
        request.user_id = user.data.id
        response = identity.add_user_to_group(request)
        print(response.status)
