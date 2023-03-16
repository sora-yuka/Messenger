from django.apps import AppConfig

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.user'

    def ready(self) -> None:
        import applications.user.signal