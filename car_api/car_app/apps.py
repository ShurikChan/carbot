from django.apps import AppConfig

class CarAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'car_app'

    def ready(self):
        import car_app.signals  # Убедитесь, что путь правильный
