from django.apps import AppConfig


class MelodymatrixConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MelodyMatrix'

    def ready(self):
        import MelodyMatrix.signals
