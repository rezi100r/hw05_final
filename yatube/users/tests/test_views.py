from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..views import SignUp


User = get_user_model()


class UsersPagesTests(TestCase):
    def setUp(self) -> None:
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client.force_login(self.user)

    def test_users_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_change'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_correct_context(self):
        """
        Шаблон signup сформированы с правильной формы
        """
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = SignUp.form_class.base_fields
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, type(expected))
