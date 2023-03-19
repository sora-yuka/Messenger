from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest import mock
from datetime import datetime, timezone
from . import tasks
from . import views
User = get_user_model()


class UserModelTest(TestCase):
    """
    Model testing
    """
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'is_active': True
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(**self.user_data)
        self.assertEqual(superuser.email, self.user_data['email'])
        self.assertTrue(superuser.check_password(self.user_data['password']))
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class UserCreateWithEmailSerializerTest(TestCase):
    """
    Serializer testing
    """
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-create-with_email')
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'password_confirm': 'testpassword'
        }
        self.invalid_payload = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'password_confirm': 'wrongpassword'
        }

    def test_create_user_with_valid_payload(self):
        response = self.client.post(self.register_url, data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_with_invalid_payload(self):
        response = self.client.post(self.register_url, data=self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserCreateWithEmailViewTestCase(APITestCase):
    """
    Views testing
    """
    def test_create_user_with_email(self):
        self.register_url = reverse('user-create-with_email')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'password_confirm': 'testpassword',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('msg', response.data)
        self.assertEqual(response.data['msg'], 'Вы успешно зарегистрировались, к вам на почту отправились письмо с активацией вашего профиля')
        user = User.objects.get(email=data['email'])
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)
        self.assertTrue(user.activation_code)
        tasks.send_email_verification_code.assert_called_once_with(data['email'], user.activation_code)


class ForgotPasswordAPIViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('forgot-password')
        self.email = 'test@example.com'
        User.objects.create_user(
            email=self.email,
            password='testpassword',
            is_active=True,
        )

    def test_valid_data(self):
        data = {'email': self.email}
        with mock.patch.object(views.tasks, 'send_password_reset_link') as mock_send_email:
            response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['msg'],
            'Мы выслали ссылку для сброса пароля.',
        )
        mock_send_email.assert_called_once_with(self.email)

    def test_invalid_data(self):
        data = {'email': 'invalidemail'}
        with mock.patch.object(views.tasks, 'send_password_reset_link') as mock_send_email:
            response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(mock_send_email.called)


class ForgotPasswordConfirmApiViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            is_active=True,
        )
        self.activation_code = self.user.create_activation_code()
        self.url = reverse('forgot-password-confirm', args=[self.activation_code])

    def test_expired_link(self):
        self.user.created_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.user.save()
        data = {'password': 'newpassword', 'password_confirm': 'newpassword'}
        with mock.patch.object(views.ForgotPasswordConfirmSerializer, 'is_valid', return_value=True), \
             mock.patch.object(views.ForgotPasswordConfirmSerializer, 'set_new_password') as mock_set_password:
            response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['msg'],
            'Ссылка для сброса пароля недействительна.',
        )
        self.assertFalse(mock_set_password.called)

    def test_valid_data(self):
        data = {'password': 'newpassword', 'password_confirm': 'newpassword'}
        with mock.patch.object(views.ForgotPasswordConfirmSerializer, 'is_valid', return_value=True), \
             mock.patch.object(views.ForgotPasswordConfirmSerializer, 'set_new_password') as mock_set_password:
            response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['msg'],
            'Пароль успешно обновлен.',
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword'))
        mock_set_password.assert_called_once()
