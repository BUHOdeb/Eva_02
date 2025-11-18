from django import forms
from .models import Reserva, Sala


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['sala', 'rut']
        widgets = {
            'sala': forms.Select(attrs={
                'class': 'form-select'
            }),
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678-9'
            }),
        }
        labels = {
            'sala': 'Sala',
            'rut': 'RUT'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar salas habilitadas
        self.fields['sala'].queryset = Sala.objects.filter(habilitada=True)

    def clean_rut(self):
        """Validación básica del RUT"""
        rut = self.cleaned_data.get('rut')
        if rut:
            rut = rut.strip().replace(' ', '').replace('.', '')
            if len(rut) < 8:
                raise forms.ValidationError("El RUT debe tener al menos 8 caracteres.")
        return rut

    def clean_sala(self):
        """Validar que la sala esté disponible"""
        sala = self.cleaned_data.get('sala')
        
        if not sala:
            raise forms.ValidationError("Debes seleccionar una sala.")
        
        if not sala.habilitada:
            raise forms.ValidationError(f"La sala {sala.nombre} no está habilitada.")
        
        if not sala.disponible:
            raise forms.ValidationError(
                f"La sala {sala.nombre} ya está reservada en este momento."
            )
        
        return sala