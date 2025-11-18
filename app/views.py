from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Sala, Reserva
from .forms import ReservaForm
from django.utils import timezone
from datetime import timedelta


def listado_salas(request):
    """Vista principal que muestra todas las salas"""
    salas = Sala.objects.all()
    return render(request, 'salas/listado.html', {'salas': salas})


def detalle_sala(request, pk):
    """Vista de detalle de una sala específica"""
    sala = get_object_or_404(Sala, pk=pk)
    reserva_activa = sala.reserva_activa
    return render(request, 'salas/detalle.html', {
        'sala': sala,
        'reserva_activa': reserva_activa
    })


def crear_reserva(request):
    """Vista para crear una nueva reserva"""
    sala_seleccionada = None
    
    # Obtener sala preseleccionada de la URL si existe
    sala_id = request.GET.get('sala')
    if sala_id:
        try:
            sala_seleccionada = Sala.objects.get(pk=sala_id)
        except Sala.DoesNotExist:
            pass

    if request.method == 'POST':
        form = ReservaForm(request.POST)

        if form.is_valid():
            reserva = form.save(commit=False)
            sala = reserva.sala
            sala_seleccionada = sala

            # 1) Verificar que la sala esté habilitada
            if not sala.habilitada:
                form.add_error('sala', "La sala no está habilitada.")
                return render(request, 'salas/reservar.html', {
                    'form': form,
                    'sala_seleccionada': sala_seleccionada
                })

            # 2) Verificar disponibilidad
            if not sala.disponible:
                form.add_error('sala', "La sala no está disponible en este momento.")
                return render(request, 'salas/reservar.html', {
                    'form': form,
                    'sala_seleccionada': sala_seleccionada
                })

            # 3) ASIGNAR FECHAS AUTOMÁTICAMENTE
            ahora = timezone.now()
            reserva.fecha_inicio = ahora
            reserva.fecha_termino = ahora + timedelta(hours=2)  # Siempre 2 horas

            # 4) Validar la reserva (duración, solapamiento, etc.)
            try:
                reserva.clean()
            except ValidationError as e:
                # Agregar los errores al formulario
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        form.add_error(field, errors)
                else:
                    form.add_error(None, e)
                
                return render(request, 'salas/reservar.html', {
                    'form': form,
                    'sala_seleccionada': sala_seleccionada
                })

            # 5) Guardar la reserva
            try:
                reserva.save()
            except Exception as e:
                form.add_error(None, f"Error al guardar la reserva: {str(e)}")
                return render(request, 'salas/reservar.html', {
                    'form': form,
                    'sala_seleccionada': sala_seleccionada
                })
            
            # 6) Mensaje de éxito y redirección
            messages.success(
                request, 
                f'¡Reserva creada exitosamente! '
                f'Sala: {sala.nombre} | '
                f'Hasta: {reserva.fecha_termino.strftime("%H:%M")}'
            )
            return redirect('salas:detalle', pk=sala.pk)
    
    else:
        # GET: Crear formulario vacío o con sala preseleccionada
        initial = {}
        if sala_seleccionada:
            initial['sala'] = sala_seleccionada
        
        form = ReservaForm(initial=initial)

    return render(request, 'salas/reservar.html', {
        'form': form,
        'sala_seleccionada': sala_seleccionada
    })