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
    #path('token/', CustomAuthToken.as_view()),   # <-- Endpoint de login
    #path('logout/', Logout.as_view()),          # <-- Endpoint de logout
]
