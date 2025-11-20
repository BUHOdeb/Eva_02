from django import forms
from .models import Reserva, Sala


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['rut', 'sala']
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678-9 o 12.345.678-9'
            }),
            'sala': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'rut': 'RUT',
            'sala': 'Sala',}
        help_texts = {'rut': 'Ingresa tu RUT con o sin puntos, pero CON guión. Ejemplo: 12345678-9',}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo salas habilitadas en el selector
        self.fields['sala'].queryset = Sala.objects.filter(habilitada=True)

    def clean_rut(self):
        """Validación y limpieza del RUT"""
        rut = self.cleaned_data.get('rut')
        if rut:
            # Limpiar el RUT (quitar espacios y puntos, convertir a mayúsculas)
            rut = rut.strip().replace(' ', '').replace('.', '').upper()
            
            # Verificar formato básico
            if '-' not in rut:
                raise forms.ValidationError(
                    "El RUT debe incluir guión. Ejemplo: 12345678-9"
                )
            
            # El validador del modelo hará el resto
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