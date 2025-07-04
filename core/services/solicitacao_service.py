import requests
import logging
from core.models import Solicitacao
from django.conf import settings
from django import forms
from ..models import Usuario

logger = logging.getLogger(__name__)
BASE_URL = settings.GERENCIAMENTO_ESCALA_API_URL + "solicitacoes"


def salvar_solicitacao(form: forms.ModelForm, usuario: Usuario) -> Solicitacao:
    """Salva uma solicitação localmente e envia para o sistema de escala."""
    # 1. Salvar localmente
    solicitacao = form.save(commit=False)
    
    # Verificar se o usuário tem tokens associados
    first_token = usuario.tokens.first()
    if not first_token:
        raise ValueError("Usuário não possui tokens associados.")
    
    # Corrigir os relacionamentos baseados no modelo
    solicitacao.cliente = first_token.contrato.cliente
    solicitacao.fornecedor = first_token.empresa
    solicitacao.usuario_solicitante = usuario
    solicitacao.save()

    # 2. Montar payload para o sistema de escala
    payload = {
        "tipoProfissional": solicitacao.tipo_profissional,
        "jornada": solicitacao.jornada,
        "observacoes": solicitacao.observacoes,
        "usuarioSolicitanteId": usuario.id,
        "cliFornecId": solicitacao.cliente.id,
        "empresaContratanteId": solicitacao.fornecedor.id,
        "contratoId": first_token.contrato_id,
    }

    # 3. Tentar enviar para o sistema de escala
    try:
        response = requests.post(
            f"{BASE_URL}/criar",
            json=payload,
            timeout=10,
        )
        if response.status_code == 200:
            logger.info("Solicitação enviada com sucesso para o sistema de escala.")
        else:
            logger.warning(
                f"Erro ao enviar solicitação para o sistema de escala: {response.status_code} - {response.text}"
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede ao conectar com o sistema de escala: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar solicitação: {str(e)}")

    return solicitacao
