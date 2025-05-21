"""
URL configuration for vehiculos_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from rest_framework import routers
from students import views_students 
from registro import views_registro
from django.contrib import admin
from students.auth import (
    SimpleLogin, SimpleLogout, StudentSearch, 
    SimpleEntry, SimpleExit, VehiculosActivos, VehiculosHistorial,
    UserRegistration
)

router = routers.DefaultRouter()
router.register(r'registros-activos', views_registro.RegistroActivoViewSet)
router.register(r'registros-historicos', views_registro.RegistroHistorialViewSet)
router.register(r'estudiantes', views_students.EstudianteViewSet, basename='estudiante')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/login/', SimpleLogin.as_view(), name='login'),
    path('api/logout/', SimpleLogout.as_view(), name='logout'),
    path('api/search/', StudentSearch.as_view(), name='student-search'),
    path('api/register/', UserRegistration.as_view(), name='register'),
    
    # Rutas de vehículos
    path('api/vehiculos/entrada/', SimpleEntry.as_view(), name='vehicle-entry'),
    path('api/vehiculos/entrada/<str:matricula>/', SimpleEntry.as_view(), name='vehicle-entry-with-matricula'),
    path('api/vehiculos/salida/', SimpleExit.as_view(), name='vehicle-exit'),
    path('api/vehiculos/salida/<str:matricula>/', SimpleExit.as_view(), name='vehicle-exit-with-matricula'),
    path('api/vehiculos/activos/<str:matricula>/', VehiculosActivos.as_view(), name='vehiculos-activos'),
    path('api/vehiculos/historial/<str:matricula>/', VehiculosHistorial.as_view(), name='vehiculos-historial'),
]
