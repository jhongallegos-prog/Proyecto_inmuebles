from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroUsuarioForm, EditarUserForm, EditarPerfilForm
from .models import Inmueble, SolicitudArriendo
from .forms import InmuebleForm
from .services import crear_solicitud_arriendo

# 1. Vista de Registro de Usuarios
def registro_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta se ha creado exitosamente.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro.html', {'form': form})


# 2. Vista de Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Sesión iniciada correctamente como {user.username}.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# 3. Vista de Logout
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


# 4. Vista de Edición de Perfil
@login_required
def perfil_view(request):
    if request.method == 'POST':
        u_form = EditarUserForm(request.POST, instance=request.user)
        p_form = EditarPerfilForm(request.POST, instance=request.user.perfil)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '¡Tus datos han sido actualizados con éxito!')
            return redirect('perfil')
    else:
        u_form = EditarUserForm(instance=request.user)
        p_form = EditarPerfilForm(instance=request.user.perfil)

    return render(request, 'perfil.html', {'u_form': u_form, 'p_form': p_form})


# 5. Vista del Dashboard Principal
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

# Decorador auxiliar para restringir acceso exclusivo a Arrendadores
def solo_arrendadores(view_func):
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'arrendador':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Acceso denegado: esta sección es exclusiva para Arrendadores.')
        return redirect('dashboard')
    return wrapper


# 1. Dashboard Principal (Lista los inmuebles según el rol)
@login_required
def dashboard_view(request):
    es_arrendador = request.user.perfil.tipo_usuario == 'arrendador'
    
    if es_arrendador:
        # El arrendador ve sus propios inmuebles
        mis_inmuebles = Inmueble.objects.filter(propietario=request.user)
        return render(request, 'dashboard.html', {
            'mis_inmuebles': mis_inmuebles,
            'es_arrendador': True
        })
    else:
        # El arrendatario ve todos los inmuebles disponibles
        inmuebles_disponibles = Inmueble.objects.filter(disponible=True)
        return render(request, 'dashboard.html', {
            'inmuebles_disponibles': inmuebles_disponibles,
            'es_arrendador': False
        })


# 2. Crear Inmueble
@login_required
@solo_arrendadores
def crear_inmueble_view(request):
    if request.method == 'POST':
        form = InmuebleForm(request.POST)
        if form.is_valid():
            inmueble = form.save(commit=False)
            inmueble.propietario = request.user  # Asigna al usuario autenticado como propietario
            inmueble.save()
            messages.success(request, f'¡Inmueble "{inmueble.nombre}" publicado con éxito!')
            return redirect('dashboard')
    else:
        form = InmuebleForm()
    return render(request, 'inmueble_form.html', {'form': form, 'titulo': 'Publicar Nuevo Inmueble'})


# 3. Editar Inmueble
@login_required
@solo_arrendadores
def editar_inmueble_view(request, pk):
    inmueble = get_object_or_404(Inmueble, pk=pk, propietario=request.user)
    if request.method == 'POST':
        form = InmuebleForm(request.POST, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, f'Inmueble "{inmueble.nombre}" actualizado correctamente.')
            return redirect('dashboard')
    else:
        form = InmuebleForm(instance=inmueble)
    return render(request, 'inmueble_form.html', {'form': form, 'titulo': f'Editar Inmueble: {inmueble.nombre}'})


# 4. Eliminar Inmueble
@login_required
@solo_arrendadores
def eliminar_inmueble_view(request, pk):
    inmueble = get_object_or_404(Inmueble, pk=pk, propietario=request.user)
    if request.method == 'POST':
        nombre = inmueble.nombre
        inmueble.delete()
        messages.warning(request, f'El inmueble "{nombre}" ha sido eliminado.')
        return redirect('dashboard')
    return render(request, 'inmueble_confirm_delete.html', {'inmueble': inmueble})


@login_required
def solicitar_arriendo_view(request, inmueble_id):
    if request.method == 'POST':
        inmueble = get_object_or_404(Inmueble, id=inmueble_id, disponible=True)

        # Pasamos directamente request.user porque la relación ForeignKey apunta a User
        existe_solicitud = SolicitudArriendo.objects.filter(
            inmueble=inmueble,
            arrendatario=request.user
        ).exists()

        if existe_solicitud:
            messages.warning(request, 'Ya tienes una solicitud de arriendo registrada para esta propiedad.')
        else:
            SolicitudArriendo.objects.create(
                inmueble=inmueble,
                arrendatario=request.user,
                estado='pendiente'
            )
            messages.success(request, f'¡Solicitud enviada exitosamente para "{inmueble.nombre}"!')

    return redirect('gestion_inmuebles:dashboard')


@login_required
def dashboard_view(request):
    es_arrendador = False
    if hasattr(request.user, 'usuario'):
        es_arrendador = request.user.usuario.tipo_usuario == 'arrendador'
    elif hasattr(request.user, 'perfil'):
        es_arrendador = request.user.perfil.tipo_usuario == 'arrendador'

    context = {
        'es_arrendador': es_arrendador,
    }

    if es_arrendador:
        context['mis_inmuebles'] = Inmueble.objects.filter(propietario=request.user)
        # Obtenemos las solicitudes enviadas a los inmuebles del arrendador
        context['solicitudes_recibidas'] = SolicitudArriendo.objects.filter(
            inmueble__propietario=request.user
        ).order_by('-fecha_solicitud')
    else:
        context['inmuebles_disponibles'] = Inmueble.objects.filter(disponible=True)
        context['mis_solicitudes'] = SolicitudArriendo.objects.filter(arrendatario=request.user)

    return render(request, 'dashboard.html', context)

@login_required
def responder_solicitud_view(request, solicitud_id, respuesta):
    solicitud = get_object_or_404(
        SolicitudArriendo, 
        id=solicitud_id, 
        inmueble__propietario=request.user
    )

    if respuesta == 'aceptar':
        solicitud.estado = 'aceptada'
        solicitud.save()
        # Opcional: Marcar la propiedad como no disponible si ya se arrendó
        inmueble = solicitud.inmueble
        inmueble.disponible = False
        inmueble.save()
        messages.success(request, f'Has aceptado la solicitud de {solicitud.arrendatario.get_full_name() or solicitud.arrendatario.username}.')

    elif respuesta == 'rechazar':
        solicitud.estado = 'rechazada'
        solicitud.save()
        messages.info(request, f'Has rechazado la solicitud para {solicitud.inmueble.nombre}.')

    return redirect('gestion_inmuebles:dashboard')

@login_required
def dashboard_view(request):
    es_arrendador = False
    if hasattr(request.user, 'usuario'):
        es_arrendador = request.user.usuario.tipo_usuario == 'arrendador'
    elif hasattr(request.user, 'perfil'):
        es_arrendador = request.user.perfil.tipo_usuario == 'arrendador'

    context = {
        'es_arrendador': es_arrendador,
    }

    if es_arrendador:
        # Propiedades del arrendador
        context['mis_inmuebles'] = Inmueble.objects.filter(propietario=request.user)
        # Solicitudes recibidas para las propiedades del arrendador
        context['solicitudes_recibidas'] = SolicitudArriendo.objects.filter(
            inmueble__propietario=request.user
        ).order_by('-id')
    else:
        # Para el arrendatario
        context['inmuebles_disponibles'] = Inmueble.objects.filter(disponible=True)
        context['mis_solicitudes'] = SolicitudArriendo.objects.filter(arrendatario=request.user)

    return render(request, 'dashboard.html', context)

@login_required
def responder_solicitud_view(request, solicitud_id, respuesta):
    """
    Permite al arrendador aceptar o rechazar una solicitud de arriendo.
    """
    solicitud = get_object_or_404(
        SolicitudArriendo, 
        id=solicitud_id, 
        inmueble__propietario=request.user
    )

    if respuesta == 'aceptar':
        solicitud.estado = 'aceptada'
        solicitud.save()
        
        # Opcional: Al aceptar la solicitud, marcamos el inmueble como 'no disponible'
        inmueble = solicitud.inmueble
        inmueble.disponible = False
        inmueble.save()

        nombre_solicitante = solicitud.arrendatario.get_full_name() or solicitud.arrendatario.username
        messages.success(request, f'¡Has aceptado la solicitud de arriendo de {nombre_solicitante}!')

    elif respuesta == 'rechazar':
        solicitud.estado = 'rechazada'
        solicitud.save()
        messages.info(request, f'Has rechazado la solicitud para el inmueble "{solicitud.inmueble.nombre}".')

    return redirect('gestion_inmuebles:dashboard')