from django.core.exceptions import ValidationError

def validar_rut(value):
    if not value:
        raise ValidationError("El RUT es requerido.")

    # Limpiar formato mínimo
    value = value.replace(".", "").replace(" ", "").upper()

    # Debe tener guion
    if "-" not in value:
        raise ValidationError("Formato inválido. Debe ser 12345678-9")

    try:
        rut, dv = value.split("-")
    except ValueError:
        raise ValidationError("Formato inválido.")

    # Antes del guion solo números
    if not rut.isdigit():
        raise ValidationError("El RUT debe contener solo números.")

    # DV solo puede ser 1–9 o K (NO 0, porque tú pediste 1 al 9)
    if dv not in ["1","2","3","4","5","6","7","8","9","K"]:
        raise ValidationError("El dígito verificador debe ser 1-9 o K.")

    return value
