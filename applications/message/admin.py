from django.contrib import admin
from applications.message.models import ChatMessage, Chat

admin.site.register(ChatMessage)
admin.site.register(Chat)