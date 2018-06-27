from django.core.management import BaseCommand

import oci
import os


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
