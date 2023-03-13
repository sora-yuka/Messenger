from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    # sender = models.ForeignKey(
    #     "User", on_delete=models.CASCADE, related_name="sent_message"
    # )
    # recipient = models.ForeignKey(
    #     "User", on_delete=models.CASCADE, related_name="received_message"
    # )
    message = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    # def __str__(self):
    #     return f"{self.sender} sent message {self.recipient}"