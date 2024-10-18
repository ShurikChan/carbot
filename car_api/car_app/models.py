from django.db import models
from django.contrib.auth.models import User


# Модель машины
class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.IntegerField()
    last_oil = models.IntegerField()

    def __str__(self):
        return f'{self.make} {self.model} ({self.year})'

# Модель для замены масла
class Oil_service(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    millage_oil = models.IntegerField(verbose_name = 'Пробег сейчас')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name ='Цена')
    name_oil = models.CharField(max_length=20, verbose_name='Название масла')
    next_millage_oil = models.IntegerField(verbose_name='Следущая замена масла')
    image = models.ImageField(upload_to='oil_images/',blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

# Модель сервиса и запчастей
class Service(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='services')
    spare_part = models.TextField()
    price_spare = models.DecimalField(max_digits=10, decimal_places=2, verbose_name ='Цена запчасти')
    price_work = models.DecimalField(max_digits=10, decimal_places=2, verbose_name ='Цена работы')
    date = models.DateTimeField(auto_now_add=True)
    images =models.ImageField(upload_to='service_image/', blank=True, null=True)


# Записи
class Note(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    image = models.ImageField(upload_to='note_image/', blank=True, null=True)

    def __str__(self):
        return f'Note for {self.car}'

class GoodSpare(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    spare_part = models.TextField()
    image = models.ImageField(upload_to='good-spare/', blank=True, null=True)
