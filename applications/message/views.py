from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from applications.message.serializers import ChatMessageSerializer
from applications.message.models import ChatMessage


class MessageViewSet(ModelViewSet):
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()
    
    def get_queryset(self):
        return super().get_queryset()