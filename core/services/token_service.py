from typing import Any
import requests
import logging

from core.models import Cliente, Fornecedor, TokenSolicitacao, Usuario
from solicitacao_escala import settings

logger = logging.getLogger(__name__)
BASE_URL = settings.GERENCIAMENTO_ESCALA_API_URL + "solicitacao-token"


def validar_token(token: str) -> Any | None:
    """Valida um token através da API externa."""
    try:
        response = requests.get(f"{BASE_URL}/validar/{token}", timeout=10)
        if response.status_code == 200:
            return response.json()
        logger.warning(f"Token validation failed with status {response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao validar token: {e}")
        return None


def associar_token(usuario: Usuario, token_str: str) -> bool:
    """Associa um token a um usuário, criando os relacionamentos necessários."""
    try:
        base_url = settings.GERENCIAMENTO_ESCALA_API_URL

        # 1. VALIDAR TOKEN
        validar_url = f"{base_url}solicitacao-token/validar/{token_str}"
        response = requests.get(validar_url, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Token validation failed: {response.status_code}")
            return False

        dados_token = response.json()

        # 2. MARCAR COMO UTILIZADO
        utilizar_url = f"{base_url}solicitacao-token/utilizar/{token_str}"
        response_utilizar = requests.put(utilizar_url, timeout=10)
        if response_utilizar.status_code != 200:
            logger.warning(f"Token utilization failed: {response_utilizar.status_code}")
            return False

        # 3. SALVAR/ATUALIZAR FORNECEDOR (empresaContratante)
        empresa = dados_token["empresaContratante"]
        fornecedor, _ = Fornecedor.objects.update_or_create(
            cnpj=empresa["cnpj"],
            defaults={
                "nome": empresa["razaoSocial"],
                "email": dados_token.get("emailCliente", ""),
                "url_sistema": base_url,  # Pode ajustar se vier outro campo apropriado
            },
        )

        # 4. SALVAR/ATUALIZAR CLIENTE (cliFornec dentro de contratoCliente)
        cli = dados_token["contratoCliente"]["cliFornec"]
        Cliente.objects.update_or_create(
            cnpj=cli["cnpj"],
            defaults={
                "nome": cli["razaoSocial"],
                "email": cli.get("email", ""),
                "telefone": cli.get("telefone", ""),
            },
        )

        # 5. CRIAR TokenSolicitacao
        TokenSolicitacao.objects.create(
            usuario=usuario,
            token=token_str,
            email_cliente=dados_token.get("emailCliente", ""),
            empresa=fornecedor,
            contrato_id=dados_token["contratoCliente"]["id"],
            utilizado=True,
        )

        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during token association: {e}")
        return False
    except KeyError as e:
        logger.error(f"Missing key in token data: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during token association: {e}")
        return False
