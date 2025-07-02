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
            "data_inicio",
            "data_fim",
            "tipo_profissional",
            "jornada",
            "observacoes",
        ]
        widgets = {
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_fim": forms.DateInput(attrs={"type": "date"}),
        }


class UsuarioCadastroForm(UserCreationForm):
    token = forms.CharField(
        required=False, help_text="Informe o token recebido (opcional)"
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


class AdicionarTokenForm(forms.Form):
    email = forms.EmailField(label="Email")
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)
    token = forms.CharField(label="Token")
