from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Solicitacao, TokenSolicitacao, Usuario
from .forms import AdicionarTokenForm, SolicitacaoForm, UsuarioCadastroForm
from .services.token_service import (
    validar_token,
    marcar_token_utilizado,
    criar_usuario,
    associar_token,
)


def login_usuario(request):
    if request.method == "POST":
        username = request.POST.get("username")
        senha = request.POST.get("senha")

        user = authenticate(request, username=username, password=senha)
        if user is not None:
            login(request, user)
            return redirect("listar_solicitacoes")
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "core/login.html")


@login_required(login_url="login")
def logout_usuario(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def listar_solicitacoes(request):
    if not request.user.is_authenticated:
        return redirect("ativar_conta")

    try:
        tokens = request.user.perfil.tokens.all()
    except Exception:
        tokens = []

    fornecedores_ids = [t.empresa_id for t in tokens]

    solicitacoes = Solicitacao.objects.select_related("cliente", "fornecedor").filter(
        fornecedor__id__in=fornecedores_ids
    )

    return render(
        request, "core/listar_solicitacoes.html", {"solicitacoes": solicitacoes}
    )


@login_required(login_url="login")
def nova_solicitacao(request):
    if request.method == "POST":
        form = SolicitacaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("listar_solicitacoes")
    else:
        form = SolicitacaoForm()
    return render(request, "core/nova_solicitacao.html", {"form": form})


def ativar_conta(request):
    token = request.GET.get("token")
    if not token:
        return render(
            request, "core/erro_token.html", {"mensagem": "Token não informado."}
        )

    dados_token = validar_token(token)
    if not dados_token:
        return render(
            request,
            "core/erro_token.html",
            {"mensagem": "Token inválido ou já utilizado."},
        )

    email = dados_token["emailCliente"]

    if request.method == "POST":
        senha = request.POST.get("senha")
        confirmar = request.POST.get("confirmar")

        if senha != confirmar:
            return render(
                request,
                "core/form_criacao_usuario.html",
                {"erro": "Senhas não conferem", "email": email, "token": token},
            )

        try:
            # Cria ou recupera o usuário Django
            user, criado = User.objects.get_or_create(
                username=email, defaults={"email": email}
            )
            if criado:
                user.set_password(senha)
                user.save()

            # Cria ou recupera perfil associado
            usuario, _ = Usuario.objects.get_or_create(
                user=user, defaults={"nome_completo": email}
            )

            # Cria vínculo com fornecedor/token
            TokenSolicitacao.objects.get_or_create(
                usuario=usuario,
                token=token,
                defaults={
                    "email_cliente": email,
                    "empresa_id": dados_token["empresaContratante"]["id"],
                    "contrato_id": dados_token["contratoCliente"]["id"],
                    "utilizado": True,
                },
            )

            login(request, user)
            marcar_token_utilizado(token)
            return redirect("listar_solicitacoes")

        except Exception as e:
            return render(
                request,
                "core/form_criacao_usuario.html",
                {
                    "erro": f"Erro ao criar usuário: {str(e)}",
                    "email": email,
                    "token": token,
                },
            )

    return render(
        request, "core/form_criacao_usuario.html", {"email": email, "token": token}
    )


def cadastro_usuario(request):
    if request.method == "POST":
        form = UsuarioCadastroForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            senha = form.cleaned_data["password1"]
            token_str = form.cleaned_data["token"]
            nome = form.cleaned_data.get("nome_completo")

            # 🔍 Verifica se usuário já existe
            user_exists = User.objects.filter(username=email).exists()

            if user_exists:
                user = authenticate(username=email, password=senha)
                if user:
                    usuario = Usuario.objects.get(user=user)
                    associar_token(usuario, token_str)
                    login(request, user)
                    return redirect("listar_solicitacoes")
                else:
                    messages.error(
                        request, "Credenciais inválidas para usuário existente."
                    )
            if not user_exists:
                # Cria novo usuário
                user, usuario = criar_usuario(form)
                associar_token(usuario, token_str)
                login(request, user)
                return redirect("listar_solicitacoes")
            else:
                messages.error(
                    request, "Usuário já cadastrado. Faça login para continuar."
                )
                return redirect("login")

    else:
        form = UsuarioCadastroForm()

    return render(request, "core/cadastro.html", {"form": form})


def adicionar_token(request):
    if request.method == "POST":
        form = AdicionarTokenForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            senha = form.cleaned_data["senha"]
            token_str = form.cleaned_data["token"]

            user = authenticate(request, username=email, password=senha)
            if user:
                usuario = user.perfil  # obtém o perfil relacionado

                sucesso = associar_token(usuario, token_str)
                if sucesso:
                    login(request, user)
                    messages.success(request, "Token adicionado com sucesso.")
                    return redirect("listar_solicitacoes")
                else:
                    messages.error(request, "Token inválido ou já utilizado.")
            else:
                messages.error(request, "Credenciais inválidas.")
    else:
        form = AdicionarTokenForm()

    return render(request, "core/adicionar_token.html", {"form": form})
