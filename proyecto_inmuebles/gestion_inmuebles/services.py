# gestion_inmuebles/services.py
from .models import SolicitudArriendo, Inmueble

def crear_solicitud_arriendo(inmueble_id, usuario):
    """
    Crea una nueva solicitud de arriendo para un inmueble si está disponible.
    """
    try:
        inmueble = Inmueble.objects.get(id=inmueble_id, disponible=True)
        # Verificar si el usuario ya envió una solicitud para esta propiedad
        ya_solicitado = SolicitudArriendo.objects.filter(
            inmueble=inmueble, 
            arrendatario=usuario
        ).exists()

        if ya_solicitado:
            return False, "Ya tienes una solicitud en proceso para esta propiedad."

        # Crear la solicitud
        SolicitudArriendo.objects.create(
            inmueble=inmueble,
            arrendatario=usuario,
            estado='pendiente'
        )
        return True, "¡Solicitud de arriendo enviada con éxito al arrendador!"
    except Inmueble.DoesNotExist:
        return False, "El inmueble no existe o ya no se encuentra disponible."