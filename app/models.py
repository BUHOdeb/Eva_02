from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .validators import validar_rut


class Sala(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    capacidad = models.PositiveIntegerField()
    habilitada = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (cap. {self.capacidad})"

    @property
    def reserva_activa(self):
        """Devuelve la reserva activa actual de la sala"""
        ahora = timezone.now()
        return self.reservas.filter(
            fecha_inicio__lte=ahora, 
            fecha_termino__gt=ahora
        ).first()

    @property
    def disponible(self):
        """Verifica si la sala está disponible para reservar"""
        return self.habilitada and self.reserva_activa is None


class Reserva(models.Model):
    rut = models.CharField(
        max_length=20, 
        validators=[validar_rut]
    )
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='reservas')
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_termino = models.DateTimeField()

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.sala.nombre} - {self.rut} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"

    def clean(self):
        """Valida que la reserva sea válida antes de guardar"""
        super().clean()
        
        # Normalizar el RUT (mayúsculas, sin espacios)
        if self.rut:
            self.rut = self.rut.upper().replace(" ", "")
        
        inicio = self.fecha_inicio
        termino = self.fecha_termino


        if not inicio or not termino:
            return

        
        if termino <= inicio:
            raise ValidationError("La fecha de término debe ser posterior a la fecha de inicio.")

        
        if (termino - inicio) > timedelta(hours=2):
            raise ValidationError("La reserva no puede durar más de 2 horas.")

        
        reservas_solapadas = self.sala.reservas.filter(
            fecha_inicio__lt=termino,
            fecha_termino__gt=inicio
        )
        
        
        if self.pk:
            reservas_solapadas = reservas_solapadas.exclude(pk=self.pk)
        
        if reservas_solapadas.exists():
            raise ValidationError(
                f"La sala ya está reservada en ese horario. "
                f"Reserva existente: {reservas_solapadas.first()}"
            )
    #paraque notenga problemas en caso dequelos 
    def save(self, *args, **kwargs):
        """Ejecuta validación completa antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)