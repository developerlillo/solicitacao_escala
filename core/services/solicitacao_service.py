import requests
from core.models import Solicitacao
from django.conf import settings
from django import forms
from ..models import Usuario

BASE_URL = settings.GERENCIAMENTO_ESCALA_API_URL + "solicitacoes"


def salvar_solicitacao(form: forms.ModelForm, usuario: Usuario) -> Solicitacao:
    # 1. Salvar localmente
    solicitacao = form.save(commit=False)
    solicitacao.cliente = (
        usuario.tokens.first().contrato.clifornec
    )  # Ajuste conforme seu relacionamento
    solicitacao.fornecedor = (
        usuario.tokens.first().empresa
    )  # Ajuste conforme seu relacionamento
    solicitacao.save()

    # 2. Montar payload para o sistema de escala
    payload = {
        "tipoProfissional": solicitacao.tipo_profissional,
        "jornada": solicitacao.jornada,
        "observacoes": solicitacao.observacoes,
        "usuarioSolicitanteId": usuario.id,
        "cliFornecId": solicitacao.cliente.id,
        "empresaContratanteId": solicitacao.fornecedor.id,
        "contratoId": usuario.tokens.first().contrato.id,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/solicitacoes/criar",
            json=payload,
            timeout=10,
        )
        if response.status_code == 200:
            print("Solicitação enviada com sucesso para o sistema de escala.")
        else:
            print(
                f"Erro ao enviar solicitação para o sistema de escala: {response.text}"
            )
    except Exception as e:
        print("Erro ao conectar com o sistema de escala:", str(e))

    return solicitacao
