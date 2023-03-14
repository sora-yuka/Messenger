from django.db import models
from app.user.managers import UserManager
import uuid
import random
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(unique=True, max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(blank=True, null=True, max_length=50, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    activation_code = models.CharField(max_length=100, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'number - {self.phone_number}, email - {self.email}'

    def create_activation_code(self):
        if self.phone_number and self.phone_number.startswith('+'):
            self.activation_code = str(random.randint(100000, 999999))
        else:
            self.activation_code = str(uuid.uuid4())

    def create_code_confirm(self):
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        code = ''
        for i in range(4):
            code += random.choice(chars)
        self.activation_code = code
