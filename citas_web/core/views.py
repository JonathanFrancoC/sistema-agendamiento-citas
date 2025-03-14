from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


def agendar_cita(request):
    return render(request, "agendamiento/agendar_cita.html")
