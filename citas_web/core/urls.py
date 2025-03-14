from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_home(request):
    return redirect("home")  # Redirige a la vista 'home' de agendamiento

urlpatterns = [
    path("admin/", admin.site.urls),
    path("agendamiento/", include("agendamiento.urls")),
    path("", redirect_to_home),  # Redirección automática a home
]