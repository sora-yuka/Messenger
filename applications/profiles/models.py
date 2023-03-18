from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=150, unique=True)
    image = models.ImageField(upload_to='images/')
    bio = models.CharField(max_length=300)
    
    def __str__(self) -> str:
        return self.user.email
    
