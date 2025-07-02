from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_usuario, name="login_default"),
    path("login/", views.login_usuario, name="login"),
    path("logout/", views.logout_usuario, name="logout"),
    path("listar", views.listar_solicitacoes, name="listar_solicitacoes"),
    path("nova/", views.nova_solicitacao, name="nova_solicitacao"),
    path("cadastro/", views.cadastro_usuario, name="cadastro_usuario"),
    path("add-token/", views.adicionar_token, name="adicionar_token"),
]
