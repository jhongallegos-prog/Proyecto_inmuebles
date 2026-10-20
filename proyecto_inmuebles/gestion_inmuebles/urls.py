from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    
    # Rutas CRUD de Inmuebles
    path('inmueble/crear/', views.crear_inmueble_view, name='crear_inmueble'),
    path('inmueble/editar/<int:pk>/', views.editar_inmueble_view, name='editar_inmueble'),
    path('inmueble/eliminar/<int:pk>/', views.eliminar_inmueble_view, name='eliminar_inmueble'),
    path('inmueble/solicitar/<int:inmueble_id>/', views.solicitar_arriendo_view, name='solicitar_arriendo'),
    path('solicitud/<int:solicitud_id>/<str:respuesta>/', views.responder_solicitud_view, name='responder_solicitud'),
]