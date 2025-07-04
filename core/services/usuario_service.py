from typing import Any
from core.models import Usuario
from django import forms


def criar_usuario(form: forms.ModelForm) -> tuple[Any, Usuario]:
    email = form.cleaned_data["email"]
    nome = form.cleaned_data["nome_completo"]

    user = form.save(commit=False)
    user.email = email
    user.username = email  # força username = email
    user.save()

    usuario = Usuario.objects.create(user=user, nome_completo=nome)
    return user, usuario
