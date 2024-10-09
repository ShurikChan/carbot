from django.urls import path, include
from rest_framework import routers
from car_app.views import CarViewSet, ServiceViewSet, NoteViewSet, PurchaseViewSet, GoodPurchaseViewSet, CreateUserView

router = routers.DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'good_purchases', GoodPurchaseViewSet)
router.register(r'register_user', CreateUserView)

urlpatterns = [
    path('', include(router.urls)),
]
