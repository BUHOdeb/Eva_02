# salas/urls.py
from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('', views.listado_salas, name='listado'),
    path('sala/<int:pk>/', views.detalle_sala, name='detalle'),
    path('reservar/', views.crear_reserva, name='crear_reserva'),
]
