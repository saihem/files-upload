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
        config = oci.config.from_file()
        identity = IdentityClient(config)
        print("DONE")
