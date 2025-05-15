from django.urls import path, include
from rest_framework import routers

from vehiculos_backend.students.auth import CustomAuthToken, Logout
from .views_students import EstudianteViewSet

router = routers.DefaultRouter()
router.register(r'estudiantes', EstudianteViewSet, basename='estudiante')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/estudiantes/buscar/', EstudianteViewSet.as_view({'get': 'buscar'}), name='estudiante-buscar'),
    path('api/', include(router.urls)),
    path('api/login/', CustomAuthToken.as_view(), name='api-login'),   # <-- Endpoint de login
    path('api/logout/', Logout.as_view(), name='api-logout'),          # <-- Endpoint de logout
]