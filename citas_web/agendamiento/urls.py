from django.urls import path
from .views import home, agendar_cita, citas_disponibles, reservar_cita, register, login_view, logout_view

urlpatterns = [
    path("", home, name="home"),
    path("agendar/", agendar_cita, name="agendar_cita"),
    path("citas/", citas_disponibles, name="citas_disponibles"),
    path("reservar/<int:cita_id>/", reservar_cita, name="reservar_cita"),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]