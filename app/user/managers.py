from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password


# class UserManager(BaseUserManager):
#     use_in_migrations = True
#
#     def _create_user(self, email, password, **extra_fields):
#         if not email:
#             raise ValueError("The given username must be set")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.password = make_password(password)
#         user.create_activation_code()
#         user.save(using=self._db)
#         return user
#
#     def create_user(self, email, password, **extra_fields):
#         extra_fields.setdefault("is_staff", False)
#         extra_fields.setdefault("is_superuser", False)
#         return self._create_user(email, password, **extra_fields)
#
#     def create_superuser(self, email, password, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         extra_fields.setdefault("is_active", True)
#
#         if extra_fields.get("is_staff") is not True:
#             raise ValueError("Superuser must have is_staff=True.")
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True.")
#
#         return self._create_user(email, password, **extra_fields)

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email and not extra_fields.get('phone_number'):
            raise ValueError("Either email or phone_number must be set")
        username = extra_fields.get('phone_number', email)
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        # user = self.model(email=email, **extra_fields)
        # user.username = username
        user.password = make_password(password)
        user.create_activation_code()
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

