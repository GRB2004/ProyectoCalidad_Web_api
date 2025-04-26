from django.urls import path, include
from rest_framework import routers
from .views_registro import RegistroActivoViewSet, RegistroHistorialViewSet

router = routers.DefaultRouter()
router.register(r'registros-activos', RegistroActivoViewSet)
router.register(r'registros-historicos', RegistroHistorialViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]