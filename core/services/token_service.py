from typing import Any
import requests

from core.models import Cliente, Fornecedor, TokenSolicitacao, Usuario
from solicitacao_escala import settings

BASE_URL = settings.GERENCIAMENTO_ESCALA_API_URL + "solicitacao-token"


def validar_token(token: str) -> Any | None:
    try:
        response = requests.get(f"{BASE_URL}/validar/{token}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print("Erro ao validar token:", e)
        return None


def associar_token(usuario: Usuario, token_str: str) -> bool:
    base_url = settings.GERENCIAMENTO_ESCALA_API_URL

    # 1. VALIDAR TOKEN
    validar_url = f"{base_url}solicitacao-token/validar/{token_str}"
    response = requests.get(validar_url)
    if response.status_code != 200:
        return False

    dados_token = response.json()

    # 2. MARCAR COMO UTILIZADO
    utilizar_url = f"{base_url}solicitacao-token/utilizar/{token_str}"
    response_utilizar = requests.put(utilizar_url)
    if response_utilizar.status_code != 200:
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
        empresa_id=fornecedor.id,
        contrato_id=dados_token["contratoCliente"]["id"],
        utilizado=True,
    )

    return True
