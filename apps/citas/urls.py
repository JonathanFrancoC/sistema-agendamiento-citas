from django.urls import path, include
from . import views

app_name = 'citas'

urlpatterns = [
    # Rutas web
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('agendar/', views.agendar_cita, name='agendar_cita'),
    path('citas/', views.citas_disponibles, name='citas_disponibles'),
    
    # Rutas API
    path('api/', include('apps.citas.api.urls')),
] 