from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Aluno


class AlunoRegistrationForm(UserCreationForm):
    curso = forms.CharField(max_length=100)
    username = forms.CharField(
        strip=False
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.TextInput(attrs={'type': 'text'}),
        help_text="Enter your password"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'curso']

    def save(self, commit=True):
        user = super(AlunoRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Aluno.objects.create(
                user=user,
                curso=self.cleaned_data.get('curso')
            )
        return user
