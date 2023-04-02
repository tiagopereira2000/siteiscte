from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Aluno, FotoPerfil


class AlunoRegistrationForm(UserCreationForm):
    curso = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'curso']


# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = FotoPerfil
#         fields = ('profile_picture',)
