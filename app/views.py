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

    # Detectar sala por GET (?sala=ID)
    sala_id = request.GET.get('sala')
    if sala_id:
        try:
            sala_seleccionada = Sala.objects.get(pk=sala_id)
        except Sala.DoesNotExist:
            sala_seleccionada = None

    # -------------------------
    #     FORM POST
    # -------------------------
    if request.method == 'POST':
        form = ReservaForm(request.POST)

        if form.is_valid():
            reserva = form.save(commit=False)
            sala = reserva.sala  # viene desde POST

            # 1. Sala habilitada
            if not sala.habilitada:
                form.add_error('sala', "La sala no está habilitada.")
                return render(request, 'salas/reservar.html', {
                    'form': form,
                    'sala_seleccionada': sala_seleccionada
                })

            # 2. Ocupada en este momento
            if sala.reserva_activa:
                form.add_error('sala', "La sala ya está reservada ahora mismo.")
                return render(request, 'salas/reservar.html', {
                    'form': form,
                    'sala_seleccionada': sala_seleccionada
                })

            # 3. Fechas automáticas
            ahora = timezone.now()
            reserva.fecha_inicio = ahora
            reserva.fecha_termino = ahora + timedelta(hours=2)

            # 4. Validación completa
            reserva.full_clean()

            # 5. Guardar reserva
            reserva.save()

            messages.success(request, "Reserva creada correctamente.")
            return redirect('salas:detalle', pk=sala.pk)

        else:
            print("❌ FORM NO VÁLIDO:", form.errors)

    # -------------------------
    #     FORM GET
    # -------------------------
    else:
        initial = {}
        if sala_seleccionada:
            initial['sala'] = sala_seleccionada

        form = ReservaForm(initial=initial)

    return render(request, 'salas/reservar.html', {
        'form': form,
        'sala_seleccionada': sala_seleccionada
    })