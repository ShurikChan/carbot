from rest_framework import viewsets
from .serializers import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Car.objects.filter(user_id=user_id)
        return Car.objects.none()

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_queryset(self):
        car_id = self.request.query_params.get('car_id')
        if car_id:
            return Service.objects.filter( car_id = car_id)
        return Service.objects.none()


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class OilViewSet(viewsets.ModelViewSet):
    queryset = Oil_service.objects.all()
    serializer_class = OilSerializer

    def get_queryset(self):
        car_id = self.request.query_params.get('car_id')
        if car_id:
            return Oil_service.objects.filter( car_id = car_id)
        return Oil_service.objects.none()


class GoodSpareViewSet(viewsets.ModelViewSet):
    queryset = GoodSpare.objects.all()
    serializer_class = GoodSpareSerializer


class CreateUserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(password=serializer.validated_data['password'])

        # Формируем ответ с данными пользователя, включая ID
        response_data = {
            'id': user.id,
            'username': user.username,
            'password': 'password123',  # Вы можете не возвращать пароль, это для примера
        }

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)



