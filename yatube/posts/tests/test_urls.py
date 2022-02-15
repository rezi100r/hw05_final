from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usr_author = User.objects.create_user(username='auth_1')
        cls.usr = User.objects.create_user(username='auth_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.usr_author,
            text='Тестовая группа',
        )
        cls.public_templates_urls = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth_1/': 'posts/profile.html',
            '/posts/' + str(cls.post.pk) + '/': 'posts/post_detail.html',
        }
        cls.private_templates_urls = {
            '/posts/' + str(cls.post.pk) + '/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.usr_author)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.usr)

    def test_posts_urls_exists_authorized_client(self):
        """
        Страницы приложения posts доступны
        авторизированному пользователю.
        """
        templates_urls = {
            **self.public_templates_urls,
            **self.private_templates_urls
        }
        for page in templates_urls:
            with self.subTest(page=page):
                response = self.authorized_client_author.get(page)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Статус ответа страницы не соответствует.'
                )

    def test_posts_urls_exists_guest_client(self):
        """Страницы приложения posts доступны гостю."""
        templates_urls = self.public_templates_urls
        for page in templates_urls.keys():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Статус ответа страницы не соответствует.'
                )

    def test_posts_urls_not_exists(self):
        """Не существующие страницы приложения posts."""
        list_urls = [
            '/group/not-exist/',
            '/profile/not-exist/',
            '/posts/not-exist/'
        ]
        for page in list_urls:
            with self.subTest(page=page):
                response = self.authorized_client_author.get(page)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND,
                    'Статус ответа страницы не соответствует.'
                )
                self.assertTemplateUsed(response, 'core/404.html')

    def test_posts_url_redirect_guest_client(self):
        """
        Страницы приложения posts доступные по
        авторизации перенаправят гостя на страницу логина.
        """
        templates_urls = self.private_templates_urls
        for page in templates_urls.keys():
            with self.subTest(page=page):
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(
                    response,
                    '/auth/login/?next=' + page,
                    msg_prefix='Перенаправление не соответствует ожидаемому'
                )

    def test_posts_urls_uses_correct_template(self):
        """URL-адрес приложения posts используют соответствующие шаблоны."""
        templates_url_names = {
            **self.public_templates_urls,
            **self.private_templates_urls
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Шаблон не соответствует ожидаемому.'
                )

    def test_posts_urls_uses_not_author(self):
        """Станица редактирования поста доступна только автору."""
        response = self.authorized_client_not_author.get(
            '/posts/' + str(self.post.pk) + '/edit/', follow=True
        )
        self.assertRedirects(
            response,
            '/posts/' + str(self.post.pk) + '/',
            msg_prefix='Перенаправление не соответствует ожидаемому'
        )
