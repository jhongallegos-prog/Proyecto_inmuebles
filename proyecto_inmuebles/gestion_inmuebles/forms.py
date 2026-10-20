from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil, TIPO_USUARIO_CHOICES
from .models import Inmueble

class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Nombres")
    last_name = forms.CharField(max_length=150, required=True, label="Apellidos")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    rut = forms.CharField(max_length=12, required=True, label="RUT")
    direccion = forms.CharField(max_length=255, required=True, label="Dirección")
    telefono = forms.CharField(max_length=20, required=True, label="Teléfono Personal")
    tipo_usuario = forms.ChoiceField(choices=TIPO_USUARIO_CHOICES, label="Tipo de Usuario")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=commit)
        # La señal post_save ya creó el Perfil, aquí lo actualizamos con los datos del formulario
        perfil = user.perfil
        perfil.rut = self.cleaned_data['rut']
        perfil.direccion = self.cleaned_data['direccion']
        perfil.telefono = self.cleaned_data['telefono']
        perfil.tipo_usuario = self.cleaned_data['tipo_usuario']
        perfil.save()
        return user


class EditarUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico'
        }


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['rut', 'direccion', 'telefono', 'tipo_usuario']
        labels = {
            'rut': 'RUT',
            'direccion': 'Dirección',
            'telefono': 'Teléfono Personal',
            'tipo_usuario': 'Tipo de Usuario'
        }

class InmuebleForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        exclude = ['propietario']  # El propietario se asignará automáticamente en la vista
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'm2_construidos': forms.NumberInput(attrs={'class': 'form-control'}),
            'm2_totales': forms.NumberInput(attrs={'class': 'form-control'}),
            'estacionamientos': forms.NumberInput(attrs={'class': 'form-control'}),
            'habitaciones': forms.NumberInput(attrs={'class': 'form-control'}),
            'banos': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_inmueble': forms.Select(attrs={'class': 'form-select'}),
            'precio_mensual': forms.NumberInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }