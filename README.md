# 🏥 Sistema de Solicitação de Escalas

Esta é uma aplicação web desenvolvida em **Django** com o objetivo de permitir que **clientes (hospitais, clínicas etc.)** realizem **solicitações de mão de obra** para **fornecedores/cooperativas** de profissionais da saúde. A aplicação está integrada ao sistema central **Gerenciamento de Escala** (Spring Boot), e se comunica via APIs para validação de tokens e envio das solicitações.

---

## 🎯 Objetivo

Permitir que hospitais ou clínicas:

- Ativem seu acesso ao sistema através de um token gerado pelo fornecedor;
- Criem usuários e associem tokens de vínculo;
- Visualizem e cadastrem **solicitações de escala** com informações como tipo de profissional, jornada, período e observações;
- Enviem essas solicitações para o sistema principal de escala para avaliação e atendimento.

---

## ⚙️ Requisitos

Antes de rodar a aplicação, certifique-se de ter instalado:

- [Python 3.10+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)
- [Git](https://git-scm.com/)
- Banco de dados configurado (ex: PostgreSQL ou SQLite3 para testes)

---

## 🚀 Como rodar o projeto localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/solicitacao-escala.git
cd solicitacao-escala
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o arquivo `.env` (opcional)

**⚠️ Importante para produção**: Crie um arquivo `.env` na raiz do projeto para configurar variáveis sensíveis:

```env
# Configurações de Segurança
SECRET_KEY=sua-chave-secreta-super-complexa-aqui
DEBUG=False

# Configurações de Banco de Dados (Produção)
DB_NAME=solicitacao_db
DB_USER=postgres
DB_PASSWORD=sua-senha-db
DB_HOST=localhost
DB_PORT=5432

# API Externa
GERENCIAMENTO_ESCALA_API_URL=http://localhost:8080/api/v1/

# Hosts permitidos (separados por vírgula)
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
```

**Para desenvolvimento**, o sistema usará SQLite automaticamente e não requer configuração adicional.

### 5. Crie e aplique as migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crie um superusuário (para acessar o admin)

```bash
python manage.py createsuperuser
```

### 7. Rode o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse em: [http://localhost:8000](http://localhost:8000)

---

## 🧩 Estrutura da aplicação

| Pasta / Arquivo      | Descrição                                                                 |
|----------------------|---------------------------------------------------------------------------|
| `core/`              | Lógica principal da aplicação, views, forms, models, templates            |
| `templates/`         | Templates HTML da interface do sistema                                    |
| `services/`          | Serviços de integração externa (ex: validação de token, envio de dados)   |
| `models.py`          | Modelos principais como `Usuario`, `Solicitacao`, `TokenSolicitacao`     |
| `views.py`           | Lógicas de autenticação, criação de usuário, listagem e envio de dados    |

---

## 🛠 Comandos úteis

### Criar uma nova app

```bash
python manage.py startapp nome_app
```

### Aplicar migrations (após alterações no model)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Criar dados para testes (fixtures)

```bash
python manage.py loaddata dados.json
```

### Acessar shell interativo do Django

```bash
python manage.py shell
```

### Executar testes

```bash
python manage.py test
```

---

## 🔧 Melhorias Implementadas

Este projeto passou por uma revisão completa para corrigir problemas e implementar melhorias:

### ✅ Correções Críticas
- **Lógica de cadastro corrigida**: Fluxo de registro de usuários funcionando corretamente
- **Configurações de segurança**: Variáveis sensíveis movidas para environment variables
- **Tratamento de erros**: Adicionado logging e tratamento adequado de exceções
- **Relacionamentos de modelos**: Corrigidos relacionamentos entre TokenSolicitacao e outras entidades

### ✅ Melhorias de Qualidade
- **Configuração de banco flexível**: SQLite para desenvolvimento, PostgreSQL para produção
- **Templates consolidados**: Removidos templates duplicados
- **Testes abrangentes**: Adicionados testes unitários e de integração
- **Logging configurado**: Sistema de logs para debugging e monitoramento

### ✅ Funcionalidades
- **Interface atualizada**: Forms com melhor UX e validação
- **Navegação melhorada**: Links e redirecionamentos consistentes
- **Mensagens de feedback**: Confirmações e erros exibidos adequadamente

---

## 🔐 Integração com sistema Gerenciamento de Escala

A aplicação consome as seguintes rotas da API do sistema de escala:

- `GET /solicitacao-token/validar/{token}` → valida se o token é válido
- `PUT /solicitacao-token/utilizar/{token}` → marca o token como utilizado
- `POST /solicitacoes/criar` → envia a solicitação para o sistema principal

---

## 🧑‍💻 Contribuindo

Se quiser sugerir melhorias ou contribuir com código, fique à vontade para abrir uma *issue* ou *pull request*.

---

## 📝 Licença

Este projeto é privado ou de uso interno. Consulte seu supervisor técnico antes de redistribuir ou reutilizar.
