from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Oil_service, Car

@receiver(post_save, sender=Oil_service)
def update_last_oil(sender, instance, **kwargs):
    # Получаем машину, для которой было добавлено обслуживание
    car = instance.car
    # Обновляем поле last_oil у машины
    car.last_oil = instance.millage_oil
    car.mileage = instance.millage_oil
    # Сохраняем изменения
    car.save()
