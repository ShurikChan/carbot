from django.urls import path, include
from django.contrib import admin
from rest_framework import routers
from car_app.views import CarViewSet, ServiceViewSet, NoteViewSet, CreateUserView, OilViewSet, GoodSpareViewSet

router = routers.DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'register_user', CreateUserView)
router.register(r'oil-service', OilViewSet)
router.register(r'good-spare', GoodSpareViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("admin/", admin.site.urls),
]
