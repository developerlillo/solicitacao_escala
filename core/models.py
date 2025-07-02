from django.db import models
from django.contrib.auth.models import User


class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18)
    email = models.EmailField()
    url_sistema = models.URLField()

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Solicitacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    tipo_profissional = models.CharField(max_length=100)
    jornada = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"Solicitação de {self.cliente.nome} para {self.fornecedor.nome}"


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    nome_completo = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_completo


class TokenSolicitacao(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="tokens"
    )
    email_cliente = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    empresa_id = models.IntegerField()
    utilizado = models.BooleanField(default=False)  # já está associado ao usuário
    contrato_id = models.IntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - Token {self.token[:8]}..."
