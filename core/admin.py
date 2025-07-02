from django.contrib import admin
from .models import Cliente, Fornecedor, Solicitacao

admin.site.register(Cliente)
admin.site.register(Fornecedor)
admin.site.register(Solicitacao)
