from django.apps import AppConfig

class RequestflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'requestflow'

    def ready(self):
        import requestflow.signals  # Ensure signals are registered
