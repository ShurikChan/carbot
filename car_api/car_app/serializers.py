from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'id']

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])  # Устанавливаем зашифрованный пароль
        user.save()
        return user


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['car', 'spare_part', 'price_spare', 'price_work', 'images', 'date']



class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


class OilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oil_service
        fields = '__all__'

class GoodSpareSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodSpare
        fields = '__all__'




