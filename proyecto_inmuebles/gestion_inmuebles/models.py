from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Opciones de configuración
TIPO_USUARIO_CHOICES = (
    ('arrendatario', 'Arrendatario'),
    ('arrendador', 'Arrendador'),
)

TIPO_INMUEBLE_CHOICES = (
    ('casa', 'Casa'),
    ('departamento', 'Departamento'),
    ('parcela', 'Parcela'),
    ('bodega', 'Bodega'),
    ('oficina', 'Oficina'),
    ('local_comercial', 'Local_Comercial'),
)

ESTADO_SOLICITUD_CHOICES = (
    ('pendiente', 'Pendiente'),
    ('aceptada', 'Aceptada'),
    ('rechazada', 'Rechazada'),
)

# 1. Extensión del modelo User
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono Personal")
    tipo_usuario = models.CharField(
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES, 
        default='arrendatario',
        verbose_name="Tipo de Usuario"
    )

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} ({self.get_tipo_usuario_display()})"


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
    else:
        Perfil.objects.create(usuario=instance)


# 2. Modelo Inmueble
class Inmueble(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    m2_construidos = models.IntegerField(verbose_name="M2 Construidos")
    m2_totales = models.IntegerField(verbose_name="M2 Totales / Terreno")
    estacionamientos = models.IntegerField(default=0, verbose_name="Estacionamientos")
    habitaciones = models.IntegerField(default=1, verbose_name="Habitaciones")
    banos = models.IntegerField(default=1, verbose_name="Baños")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    comuna = models.CharField(max_length=100, verbose_name="Comuna")
    region = models.CharField(max_length=100, verbose_name="Región")
    tipo_inmueble = models.CharField(
        max_length=20, 
        choices=TIPO_INMUEBLE_CHOICES, 
        default='departamento',
        verbose_name="Tipo de Inmueble"
    )
    precio_mensual = models.IntegerField(verbose_name="Precio Mensual ($)")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    propietario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='inmuebles',
        verbose_name="Arrendador / Propietario"
    )

    def __str__(self):
        return f"{self.nombre} - {self.comuna} (${self.precio_mensual:,})"


# 3. Modelo Solicitud de Arriendo
class SolicitudArriendo(models.Model):
    inmueble = models.ForeignKey(
        Inmueble, 
        on_delete=models.CASCADE, 
        related_name='solicitudes',
        verbose_name="Inmueble"
    )
    arrendatario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='solicitudes',
        verbose_name="Arrendatario"
    )
    mensaje = models.TextField(blank=True, null=True, verbose_name="Mensaje opcional")
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_SOLICITUD_CHOICES, 
        default='pendiente',
        verbose_name="Estado de Solicitud"
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")

    def __str__(self):
        return f"Solicitud de {self.arrendatario.username} para {self.inmueble.nombre}"

class Region(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="comunas"
    )

    def __str__(self):
        return f"{self.nombre} - {self.region.nombre}"

    class Meta:
        verbose_name = "Comuna"
        verbose_name_plural = "Comunas"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "region"],
                name="unique_comuna_por_region"
            )
        ]