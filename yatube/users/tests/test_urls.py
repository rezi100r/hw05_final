from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_exists_authorized_client(self):
        """
        Страницы приложения users доступны
        авторизированному пользователю.
        """
        list_urls = [
            '/auth/login/',
            '/auth/signup/',
            '/auth/password_change/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
            '/auth/logout/',
            '/auth/signup/',
        ]
        for page in list_urls:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_users_urls_uses_correct_template(self):
        """URL-адрес приложения users используют соответствующие шаблоны."""
        templates_url_names = {
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
