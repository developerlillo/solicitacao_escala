from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from core.models import Usuario, Cliente, Fornecedor, Contrato, TokenSolicitacao, Solicitacao
from core.forms import UsuarioCadastroForm
from core.services.token_service import associar_token
from core.services.usuario_service import criar_usuario


class ModelTestCase(TestCase):
    """Test case for models."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo='Test User'
        )
        self.cliente = Cliente.objects.create(
            nome='Test Client',
            cnpj='12345678901234',
            email='client@test.com',
            telefone='123456789'
        )
        self.fornecedor = Fornecedor.objects.create(
            nome='Test Provider',
            cnpj='98765432109876',
            email='provider@test.com',
            url_sistema='http://test.com'
        )
        self.contrato = Contrato.objects.create(
            numero='123',
            cliente=self.cliente,
            fornecedor=self.fornecedor
        )
    
    def test_usuario_str(self):
        """Test Usuario string representation."""
        self.assertEqual(str(self.usuario), 'Test User')
    
    def test_cliente_str(self):
        """Test Cliente string representation."""
        self.assertEqual(str(self.cliente), 'Test Client')
    
    def test_fornecedor_str(self):
        """Test Fornecedor string representation."""
        self.assertEqual(str(self.fornecedor), 'Test Provider')


class ViewTestCase(TestCase):
    """Test case for views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            nome_completo='Test User'
        )
    
    def test_login_view_get(self):
        """Test login view GET request."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        """Test login view POST request with valid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'senha': 'testpass123'
        })
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
    
    def test_login_view_post_invalid(self):
        """Test login view POST request with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'senha': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuário ou senha inválidos')
    
    def test_cadastro_usuario_view_get(self):
        """Test cadastro_usuario view GET request."""
        response = self.client.get(reverse('cadastro_usuario'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro')


class FormTestCase(TestCase):
    """Test case for forms."""
    
    def test_usuario_cadastro_form_valid(self):
        """Test UsuarioCadastroForm with valid data."""
        form_data = {
            'email': 'newuser@example.com',
            'nome_completo': 'New User',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'token': 'test-token-123'
        }
        form = UsuarioCadastroForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_usuario_cadastro_form_invalid_passwords(self):
        """Test UsuarioCadastroForm with mismatched passwords."""
        form_data = {
            'email': 'newuser@example.com',
            'nome_completo': 'New User',
            'password1': 'complexpass123',
            'password2': 'differentpass456',
            'token': 'test-token-123'
        }
        form = UsuarioCadastroForm(data=form_data)
        self.assertFalse(form.is_valid())


class ServiceTestCase(TestCase):
    """Test case for services."""
    
    def test_criar_usuario(self):
        """Test criar_usuario service."""
        form_data = {
            'email': 'newuser@example.com',
            'nome_completo': 'New User',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'token': 'test-token-123'
        }
        form = UsuarioCadastroForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user, usuario = criar_usuario(form)
        
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.username, 'newuser@example.com')
        self.assertEqual(usuario.nome_completo, 'New User')
    
    @patch('requests.get')
    @patch('requests.put')
    def test_associar_token_success(self, mock_put, mock_get):
        """Test associar_token service with successful API calls."""
        # Create required objects first
        cliente = Cliente.objects.create(
            nome='Test Client',
            cnpj='98765432109876',
            email='client@test.com',
            telefone='123456789'
        )
        fornecedor = Fornecedor.objects.create(
            nome='Test Company',
            cnpj='12345678901234',
            email='company@test.com',
            url_sistema='http://test.com'
        )
        contrato = Contrato.objects.create(
            id=1,
            numero='123',
            cliente=cliente,
            fornecedor=fornecedor
        )
        
        # Mock API responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'emailCliente': 'client@test.com',
            'empresaContratante': {
                'cnpj': '12345678901234',
                'razaoSocial': 'Test Company'
            },
            'contratoCliente': {
                'id': 1,
                'cliFornec': {
                    'cnpj': '98765432109876',
                    'razaoSocial': 'Test Client',
                    'email': 'client@test.com',
                    'telefone': '123456789'
                }
            }
        }
        mock_put.return_value.status_code = 200
        
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        usuario = Usuario.objects.create(
            user=user,
            nome_completo='Test User'
        )
        
        result = associar_token(usuario, 'test-token')
        self.assertTrue(result)
        
        # Check that token was created
        token = TokenSolicitacao.objects.filter(usuario=usuario).first()
        self.assertIsNotNone(token)
        self.assertEqual(token.token, 'test-token')
    
    @patch('requests.get')
    def test_associar_token_failure(self, mock_get):
        """Test associar_token service with failed API call."""
        mock_get.return_value.status_code = 404
        
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        usuario = Usuario.objects.create(
            user=user,
            nome_completo='Test User'
        )
        
        result = associar_token(usuario, 'invalid-token')
        self.assertFalse(result)


class IntegrationTestCase(TestCase):
    """Integration tests for the complete flow."""
    
    def setUp(self):
        """Set up test data."""
        # Create required objects for the token association
        self.cliente = Cliente.objects.create(
            nome='Test Client',
            cnpj='98765432109876',
            email='client@test.com',
            telefone='123456789'
        )
        self.fornecedor = Fornecedor.objects.create(
            nome='Test Company',
            cnpj='12345678901234',
            email='company@test.com',
            url_sistema='http://test.com'
        )
        self.contrato = Contrato.objects.create(
            id=1,
            numero='123',
            cliente=self.cliente,
            fornecedor=self.fornecedor
        )
    
    @patch('core.services.token_service.requests.get')
    @patch('core.services.token_service.requests.put')
    def test_cadastro_usuario_flow_new_user(self, mock_put, mock_get):
        """Test complete user registration flow for new user."""
        # Mock API responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'emailCliente': 'client@test.com',
            'empresaContratante': {
                'cnpj': '12345678901234',
                'razaoSocial': 'Test Company'
            },
            'contratoCliente': {
                'id': 1,
                'cliFornec': {
                    'cnpj': '98765432109876',
                    'razaoSocial': 'Test Client',
                    'email': 'client@test.com',
                    'telefone': '123456789'
                }
            }
        }
        mock_put.return_value.status_code = 200
        
        response = self.client.post(reverse('cadastro_usuario'), {
            'email': 'newuser@example.com',
            'nome_completo': 'New User',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'token': 'test-token-123'
        })
        
        # Should redirect to listar_solicitacoes after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_solicitacoes'))
        
        # Check user was created
        user = User.objects.filter(email='newuser@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser@example.com')
        
        # Check usuario profile was created
        usuario = Usuario.objects.filter(user=user).first()
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.nome_completo, 'New User')
    
    @patch('core.services.token_service.requests.get')
    @patch('core.services.token_service.requests.put')
    def test_cadastro_usuario_flow_existing_user(self, mock_put, mock_get):
        """Test complete user registration flow for existing user."""
        # Mock API responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'emailCliente': 'client@test.com',
            'empresaContratante': {
                'cnpj': '12345678901234',
                'razaoSocial': 'Test Company'
            },
            'contratoCliente': {
                'id': 1,
                'cliFornec': {
                    'cnpj': '98765432109876',
                    'razaoSocial': 'Test Client',
                    'email': 'client@test.com',
                    'telefone': '123456789'
                }
            }
        }
        mock_put.return_value.status_code = 200
        
        # Create existing user
        existing_user = User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='existingpass123'
        )
        existing_usuario = Usuario.objects.create(
            user=existing_user,
            nome_completo='Existing User'
        )
        
        response = self.client.post(reverse('cadastro_usuario'), {
            'email': 'existing@example.com',
            'nome_completo': 'Existing User',
            'password1': 'existingpass123',
            'password2': 'existingpass123',
            'token': 'test-token-123'
        })
        
        # Should redirect to listar_solicitacoes after successful token association
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_solicitacoes'))
