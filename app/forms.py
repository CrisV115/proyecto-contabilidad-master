from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from django.core.exceptions import ValidationError
import re

class RegistroForm(UserCreationForm):

    telefono = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 0991234567',
            'pattern': '[0-9]{10}',
            'maxlength': '10',
            'title': 'Ingrese exactamente 10 números',
        })
    )

    pregunta_seguridad = forms.ChoiceField(
        choices=Usuario.PREGUNTAS
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'telefono',
            'password1',
            'password2',
            'pregunta_seguridad',
            'respuesta_seguridad'
        ]

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not re.fullmatch(r'\d{10}', telefono):
            raise ValidationError("El teléfono debe tener exactamente 10 números.")

        return telefono
