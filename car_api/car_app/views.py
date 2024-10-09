from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework import viewsets, generics
from .models import Car, Service, Note, Purchase, GoodPurchase
from .serializers import CarSerializer, ServiceSerializer, NoteSerializer, PurchaseSerializer, GoodPurchaseSerializer
from django.contrib.auth.models import User


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


class GoodPurchaseViewSet(viewsets.ModelViewSet):
    queryset = GoodPurchase.objects.all()
    serializer_class = GoodPurchaseSerializer


class CreateUserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        password = serializer.validated_data['password']
        user = serializer.save(password=password)
