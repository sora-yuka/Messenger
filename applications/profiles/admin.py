from django.contrib import admin

from applications.profiles.models import UserProfile

# Register your models here.
admin.site.register(UserProfile)