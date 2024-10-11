from rest_framework import serializers
from .models import Car, Service, Note, Purchase, GoodPurchase
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class CarSerializer(serializers.ModelSerializer):
    user = serializers.CharField()

    class Meta:
        model = Car
        fields = '__all__'

    def create(self, validated_data):
        username = validated_data.pop('user')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'user': 'User with this username does not exist.'})
        car = Car.objects.create(user=user, **validated_data)
        return car


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


class GoodPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodPurchase
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
