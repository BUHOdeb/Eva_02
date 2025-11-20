from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from .models import Sala, Reserva
from .forms import ReservaForm



def listado_salas(request):
    #Retorna todas las propiedades de las salas parapoder iterarlas en el listado html 
    
    salas = Sala.objects.all()
    return render(request, 'salas/listado.html', {'salas': salas})


def detalle_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    
    reserva_actual = sala.reserva_activa
    
    return render(request, 'salas/detalle.html', {
        'sala': sala,
        'reserva_actual': reserva_actual
    })

#El crear_reserva tiene dos funciones mostrar el template del formulario Si viene por GET
# y procesarlo cuando el usuario loenvia por POST

def crear_reserva(request):

    #detecta la url de la sala enlaque ingreso el usuario y la procesa con la variable
    #esto hace que la 'sala'en el form se ingrese automaticamente si noexiste tira none

    sala_seleccionada = None
    sala_id = request.GET.get('sala')
    if sala_id:
        try:
            sala_seleccionada = Sala.objects.get(pk=sala_id)
        except Sala.DoesNotExist:
            sala_seleccionada = None

    if request.method == 'POST':
        form = ReservaForm(request.POST)

        if form.is_valid():
            reserva = form.save(commit=False)
            sala = reserva.sala 

            
            if not sala.habilitada:
                form.add_error('sala', "La sala no está habilitada.")
                return render(request, 'salas/reservar.html', {
                    'form': form,
                    'sala_seleccionada': sala_seleccionada
                })

            
            if sala.reserva_activa:
                form.add_error('sala', "La sala ya está reservada ahora mismo.")
                return render(request, 'salas/reservar.html', {
                    'form': form,
                    'sala_seleccionada': sala_seleccionada
                })

            #fechas automáticas
            ahora = timezone.now()
            reserva.fecha_inicio = ahora
            reserva.fecha_termino = ahora + timedelta(hours=2)

            #validación completa
            reserva.full_clean()

            #guardar reserva
            reserva.save()

            messages.success(request, "Reserva creada correctamente.")
            return redirect('salas:detalle', pk=sala.pk)

        else:
            print("FORM NO VÁLIDO:", form.errors)


    else:
        initial = {}
        if sala_seleccionada:
            initial['sala'] = sala_seleccionada

        form = ReservaForm(initial=initial)

    return render(request, 'salas/reservar.html', {
        'form': form,
        'sala_seleccionada': sala_seleccionada
    })