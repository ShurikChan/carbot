from django.db import models
from django.contrib.auth.models import User


class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    mileage = models.IntegerField()

    def __str__(self):
        return f'{self.make} {self.model} ({self.year})'


class Service(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=100)
    last_service_date = models.DateField()

    def __str__(self):
        return f'{self.service_type} for {self.car} on {self.last_service_date}'


class Note(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()

    def __str__(self):
        return f'Note for {self.car}'


class Purchase(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='purchases')
    item = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()

    def __str__(self):
        return f'{self.item} for {self.car} on {self.purchase_date}'


class GoodPurchase(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='good_purchases')
    item = models.CharField(max_length=100)
    image = models.ImageField(upload_to='good_purchases/')

    def __str__(self):
        return f'Good purchase: {self.item} for {self.car}'
