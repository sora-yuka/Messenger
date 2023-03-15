from django.db import models
from django.contrib.auth import get_user_model
from applications.user.models import User

# User = get_user_model()


class Chat(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_owner'
    )
    current_members = models.ManyToManyField(
        User, blank=True, related_name='current_members'
    )
    title = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return f'Chat {self.title}, owner {self.owner}'
    

class ChatMessage(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_chat_message'
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.sender} sent message {self.chat}'
    

class PrivateMessage(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='related_name'
    )
    recipient = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='sent_private_message'
    )
    message = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.sender} send message to {self.recipient}'