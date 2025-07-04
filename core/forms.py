from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import Solicitacao


class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = [
            "cliente",
            "fornecedor",
            "tipo_profissional",
            "jornada",
            "observacoes",
        ]


class UsuarioCadastroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    token = forms.CharField(
        required=True, help_text="Informe o token recebido"
    )
    nome_completo = forms.CharField(required=True, label="Nome Completo")

    class Meta:
        model = User
        fields = [
            "email",
            "nome_completo",
            "password1",
            "password2",
            "token",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            # Allow existing users to re-use their email for token association
            pass
        return email


class AdicionarTokenForm(forms.Form):
    email = forms.EmailField(label="Email")
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)
    token = forms.CharField(label="Token")
