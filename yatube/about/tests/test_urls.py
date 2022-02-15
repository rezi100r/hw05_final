from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_author_page(self):
        """Страницы приложения about доступны гостю."""
        list_urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for page in list_urls:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
