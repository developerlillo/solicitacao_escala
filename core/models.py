from django.db import models
from django.contrib.auth.models import User


# (Empresa no gerenciamento de escala)
class Fornecedor(
    models.Model
):  # armazena informações sobre os fornecedores, que são empresas que oferecem serviços para o cliente
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18)
    email = models.EmailField()
    url_sistema = models.URLField()

    def __str__(self):
        return self.nome


# (CliFornec no gerenciamento de escala)
class Cliente(
    models.Model
):  # armazena informações sobre o cliente, terá apenas um registro
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    nome_completo = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_completo


# (ContratoCapa no gerenciamento de escala)
class Contrato(models.Model):
    id = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=100)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)

    def __str__(self):
        return f"Contrato {self.numero} - {self.cliente.nome} x {self.fornecedor.nome}"


# (SolicitacaoToken no gerenciamento de escala)
class TokenSolicitacao(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="tokens"
    )
    token = models.CharField(max_length=64, unique=True)
    email_cliente = models.EmailField(blank=True)
    empresa = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, null=True, blank=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    utilizado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - Token {self.token[:8]}..."


# (Solicitacao no gerenciamento de escala)
class Solicitacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    usuario_solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    data_solicitacao = models.DateTimeField(auto_now_add=True)
    tipo_profissional = models.CharField(max_length=100)
    jornada = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"Solicitação de {self.cliente.nome} para {self.fornecedor.nome}"
