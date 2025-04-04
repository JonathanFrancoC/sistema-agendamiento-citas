from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='api_register'),
    path('login/', views.login_user, name='api_login'),
    path('citas/', views.listar_citas, name='api_listar_citas'),
    path('citas/crear/', views.crear_cita, name='api_crear_cita'),
] 