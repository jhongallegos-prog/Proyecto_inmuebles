from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil, Inmueble, SolicitudArriendo

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'

class UserAdmin(BaseUserAdmin):
    inlines = [PerfilInline]

@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_inmueble', 'comuna', 'region', 'precio_mensual', 'disponible', 'propietario')
    list_filter = ('tipo_inmueble', 'comuna', 'region', 'disponible')
    search_fields = ('nombre', 'direccion', 'comuna', 'region')

@admin.register(SolicitudArriendo)
class SolicitudArriendoAdmin(admin.ModelAdmin):
    list_display = ('inmueble', 'arrendatario', 'estado', 'fecha_solicitud')
    list_filter = ('estado', 'fecha_solicitud')
    search_fields = ('inmueble__nombre', 'arrendatario__username')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Perfil)

