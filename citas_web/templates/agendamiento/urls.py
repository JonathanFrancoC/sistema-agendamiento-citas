from django.urls import path
from .views import agendar_cita

urlpatterns = [
    path("agendar/", agendar_cita, name="agendar_cita"),
]
