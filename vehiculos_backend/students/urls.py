from django.urls import path, include
from rest_framework import routers
from .views_students import EstudianteViewSet

router = routers.DefaultRouter()
router.register(r'estudiantes', EstudianteViewSet, basename='estudiante')

urlpatterns = [
    path('api/', include(router.urls)),
]