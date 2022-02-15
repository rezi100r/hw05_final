from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UserCreateFormTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='auth')
        self.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Пользователь',
            'last_name': 'Тестовый',
            'username': 'testing_user',
            'email': 'testing_user@test.com',
            'password1': 'password_testUser',
            'password2': 'password_testUser',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(username='testing_user').exists()
        )
