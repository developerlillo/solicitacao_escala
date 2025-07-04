from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Solicitacao, Usuario
from .forms import AdicionarTokenForm, SolicitacaoForm, UsuarioCadastroForm
from .services.token_service import associar_token
from .services.usuario_service import criar_usuario
from .services.solicitacao_service import salvar_solicitacao


def login_usuario(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
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
def logout_usuario(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def listar_solicitacoes(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    if not request.user.is_authenticated:
        return redirect("ativar_conta")

    try:
        tokens = request.user.perfil.tokens.all()  # type: ignore
    except Exception:
        tokens = []

    fornecedores_ids = [t.empresa_id for t in tokens]  # type: ignore

    solicitacoes = Solicitacao.objects.select_related("cliente", "fornecedor").filter(
        fornecedor__id__in=fornecedores_ids
    )

    return render(
        request, "core/listar_solicitacoes.html", {"solicitacoes": solicitacoes}
    )


# @login_required(login_url="login")
# def nova_solicitacao(
#     request: HttpRequest,
# ) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
#     if request.method == "POST":
#         form = SolicitacaoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("listar_solicitacoes")
#     else:
#         form = SolicitacaoForm()
#     return render(request, "core/nova_solicitacao.html", {"form": form})


@login_required(login_url="login")
def nova_solicitacao(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    if request.method == "POST":
        form = SolicitacaoForm(request.POST)
        if form.is_valid():
            try:
                usuario: Usuario = request.user.perfil  # type: ignore
                salvar_solicitacao(form, usuario)  # type: ignore
                messages.success(request, "Solicitação criada com sucesso!")
                return redirect("listar_solicitacoes")
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Erro ao criar solicitação: {str(e)}")
    else:
        form = SolicitacaoForm()
    return render(request, "core/nova_solicitacao.html", {"form": form})


def cadastro_usuario(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
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
                    sucesso = associar_token(usuario, token_str)
                    if sucesso:
                        login(request, user)
                        messages.success(request, "Token associado com sucesso!")
                        return redirect("listar_solicitacoes")
                    else:
                        messages.error(request, "Token inválido ou já utilizado.")
                else:
                    messages.error(
                        request, "Credenciais inválidas para usuário existente."
                    )
            else:
                # Cria novo usuário
                try:
                    user, usuario = criar_usuario(form)
                    sucesso = associar_token(usuario, token_str)
                    if sucesso:
                        login(request, user)
                        messages.success(request, "Usuário cadastrado com sucesso!")
                        return redirect("listar_solicitacoes")
                    else:
                        # Remove o usuário criado se o token for inválido
                        user.delete()
                        messages.error(request, "Token inválido. Usuário não foi criado.")
                except Exception as e:
                    messages.error(request, f"Erro ao criar usuário: {str(e)}")

    else:
        form = UsuarioCadastroForm()

    return render(request, "core/cadastro.html", {"form": form})


def adicionar_token(
    request: HttpRequest,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse:
    if request.method == "POST":
        form = AdicionarTokenForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            senha = form.cleaned_data["senha"]
            token_str = form.cleaned_data["token"]

            user = authenticate(request, username=email, password=senha)
            if user:
                usuario = Usuario.objects.get(user=user)

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
