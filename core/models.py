from django.db import models
from django.contrib.auth.models import User

class Owner(User):
    login_id = models.CharField(max_length=5, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_owner'

class File(models.Model):
    name = models.CharField(max_length=1000)
    bucket = models.CharField(null=True, max_length=1000)
    size = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(Owner, models.CASCADE, 'owner')

    class Meta:
        db_table = 'core_file'
