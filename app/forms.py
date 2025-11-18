from django import forms
from .models import Reserva, Sala
from django.utils import timezone
from datetime import timedelta


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        # SOLO rut y sala - fecha_termino se asigna automáticamente
        fields = ['rut', 'sala']
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12.345.678-9'
            }),
            'sala': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'rut': 'RUT',
            'sala': 'Sala',
        }
        help_texts = {
            'rut': 'Ingresa tu RUT sin puntos y con guión',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo salas habilitadas en el selector
        self.fields['sala'].queryset = Sala.objects.filter(habilitada=True)

    def clean_rut(self):
        """Validación básica del RUT"""
        rut = self.cleaned_data.get('rut')
        if rut:
            # Limpiar el RUT (quitar espacios y puntos)
            rut = rut.strip().replace(' ', '').replace('.', '')
            if len(rut) < 8:
                raise forms.ValidationError("El RUT debe tener al menos 8 caracteres.")
        return rut

    def clean(self):
        """Validación del formulario completo"""
        cleaned = super().clean()
        sala = cleaned.get('sala')
        
        if sala:
            # Verificar que la sala esté disponible AHORA
            if not sala.disponible:
                raise forms.ValidationError(
                    "La sala no está disponible en este momento. "
                    "Por favor elige otra sala."
                )
        
        return cleaned