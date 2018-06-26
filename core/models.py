from django.db import models


class Owner(models.Model):
    login_id = models.UUIDField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    is_authenticated = True
    is_anonymous = False
    USERNAME_FIELD = 'login_id'
    REQUIRED_FIELDS = ()

    class Meta:
        db_table = 'core_owner'


class File(models.Model):
    file = models.FileField()
    name = models.CharField(max_length=1000, null=True)
    bucket = models.CharField(null=True, max_length=1000)
    size = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(Owner, models.CASCADE, 'owner')

    class Meta:
        db_table = 'core_file'

