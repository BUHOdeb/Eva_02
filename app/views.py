from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta

from .models import Sala, Reserva
from .forms import ReservaForm


# ---------------------------------------
# LISTADO DE SALAS
# ---------------------------------------
def listado_salas(request):
    salas = Sala.objects.all()
    return render(request, 'salas/listado.html', {'salas': salas})


# ---------------------------------------
# DETALLE DE SALA
# ---------------------------------------
def detalle_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    reserva_actual = sala.reserva_activa
    return render(request, 'salas/detalle.html', {
        'sala': sala,
        'reserva_actual': reserva_actual
    })


# ---------------------------------------
# CREAR RESERVA
# ---------------------------------------
def crear_reserva(request):
    """Vista para crear una nueva reserva"""
    
    sala_seleccionada = None
    
    # Obtener sala seleccionada vía GET
    sala_id = request.GET.get('sala')
    if sala_id:
        try:
            sala_seleccionada = Sala.objects.get(pk=sala_id)
        except Sala.DoesNotExist:
            sala_seleccionada = None

    # ---- GET: mostrar formulario ----
    if request.method == 'GET':
        form = ReservaForm()
        
        # Si viene sala pre-seleccionada, fijarla en el form
        if sala_seleccionada:
            form.fields['sala'].initial = sala_seleccionada.pk
        
        return render(request, 'salas/reservar.html', {
            'form': form,
            'sala_seleccionada': sala_seleccionada
        })

    # ---- POST: guardar reserva ----
    form = ReservaForm(request.POST)

    if form.is_valid():
        reserva = form.save(commit=False)
        sala = reserva.sala  # sala escogida en el form

        # Validaciones
        if not sala.habilitada:
            form.add_error('sala', "La sala no está habilitada.")
            return render(request, 'salas/reservar.html', {
                'form': form,
                'sala_seleccionada': sala
            })

        if sala.reserva_activa:
            form.add_error('sala', "La sala ya está reservada ahora mismo.")
            return render(request, 'salas/reservar.html', {
                'form': form,
                'sala_seleccionada': sala
            })

        # Asignar las fechas (2 horas)
        ahora = timezone.now()
        reserva.fecha_inicio = ahora
        reserva.fecha_termino = ahora + timedelta(hours=2)

        reserva.full_clean()
        reserva.save()

        messages.success(request, "Reserva creada correctamente.")
        return redirect('salas:detalle', pk=sala.pk)

    # Si el form no es válido
    return render(request, 'salas/reservar.html', {
        'form': form,
        'sala_seleccionada': sala_seleccionada
    })
