from django.contrib import admin
from .models import Owner, File
# Register your models here.


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass
