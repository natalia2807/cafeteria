from django import forms
from .models import Producto
from .models import Estudiante
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'valor', 'cantidad', 'categoria','imagen', 'categoria', 'fecha_vencimiento', 'fecha_entrega']

    categoria = forms.ChoiceField(choices=Producto.CATEGORIA_CHOICES)

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['cedula_estudiante', 'nombre', 'correoEstudiante', 'correoAcudiente','tipo_usuario']
      


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']