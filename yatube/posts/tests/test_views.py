import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.core.cache import cache
from django.urls import reverse
from http import HTTPStatus

from ..models import Post, Group, User, Follow
from ..forms import PostForm


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.usr_author = User.objects.create_user(username='auth_1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.usr_author,
            text='Тестовая группа',
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=False)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.usr_author)

    def test_posts_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.usr_author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Namespace не использует нужный шаблон.'
                )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Статус ответа страницы не соответствует.'
        )
        check_post = response.context.get('post')
        self.assertEqual(check_post.text, 'Тестовая группа')
        self.assertEqual(check_post.author, self.usr_author)
        self.assertEqual(check_post.group, self.group)
        self.assertEqual(check_post.pk, self.post.pk)
        self.assertEqual(check_post.pub_date, self.post.pub_date)
        self.assertIn(self.uploaded.name, check_post.image.name)

    def test_post_edit_and_create_correct_context(self):
        """
        Шаблон post_edit и post_create сформированы с правильной формы
        """
        post_form = PostForm()
        templates_pages_names = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(
                    'form',
                    response.context,
                    'На странице нет формы'
                )
                self.assertIsInstance(
                    response.context['form'],
                    type(post_form),
                    'Форма не соответствует ожидаемой'
                )

    def test_post_create_show_in_pages(self):
        """Отображение созданого поста на index, profile, group_list"""
        templates_pages_names = [
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': self.usr_author.username}
            ),
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn('page_obj', response.context)
                page_obj = response.context['page_obj']
                self.assertEqual(page_obj[0].pk, self.post.pk)
                self.assertIn(
                    self.uploaded.name,
                    page_obj[0].image.name,
                )
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug-2'}
            )
        )
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_cache_index_page(self):
        """Тестирование использование кеширования"""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_check = response.content
        post = Post.objects.get(pk=1)
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cache_check)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cache_check)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.usr_author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [Post.objects.create(
            author=cls.usr_author,
            text='Тестовая запись',
            group=cls.group
        ) for i in range(13)]

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.usr_author)

    def test_first_page_contains_ten_records(self):
        """
        Проверка пагинатора первой страницы и проверка выводимой информации
        """
        templates_pages_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.usr_author.username}
            )
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn('page_obj', response.context)
                self.assertEqual(len(response.context['page_obj']), 10)
                first_object = response.context.get('page_obj').object_list[0]
                post_text_0 = first_object.text
                post_group_0 = first_object.group.title
                post_author_0 = first_object.author.username
                self.assertEqual(post_text_0, 'Тестовая запись')
                self.assertEqual(post_group_0, 'Тестовая группа')
                self.assertEqual(post_author_0, self.usr_author.username)

    def test_second_page_contains_three_records(self):
        """Проверка пагинатора второй страницы"""
        templates_pages_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.usr_author.username}
            )
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name + '?page=2'
                )
                self.assertIn('page_obj', response.context)
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_show_correct_context(self):
        """Список постов отфильтрованых по группе"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            )
        )
        self.assertIn('page_obj', response.context)
        for post in response.context.get('page_obj').object_list:
            self.assertEqual(post.group, self.group)

    def test_profile_show_correct_context(self):
        """Список постов отфильтрованых по автору"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.usr_author.username}
            )
        )
        self.assertIn('page_obj', response.context)
        for post in response.context.get('page_obj').object_list:
            self.assertEqual(post.author.username, self.usr_author.username)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.usr_author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='auth_1')
        cls.user_2 = User.objects.create_user(username='auth_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [Post.objects.create(
            author=cls.usr_author,
            text='Тестовая запись',
            group=cls.group
        ) for i in range(13)]

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_follow_authorized_client(self):
        """Тестирование подписки и отписки"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.usr_author.username}
            )
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            'Статус ответа страницы не соответствует.'
        )
        follow = Follow.objects.get(user=self.user)
        self.assertEqual(follow.author, self.usr_author)
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.usr_author.username}
            )
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            'Статус ответа страницы не соответствует.'
        )
        follow = Follow.objects.filter(user=self.user)
        self.assertEqual(len(follow), 0)

    def test_follow_view_post(self):
        """Публикация постов в избранных пользователя с подпиской на автора"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.usr_author.username}
            )
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            'Статус ответа страницы не соответствует.'
        )
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index',
            )
        )
        post = response.context['page_obj'][0]
        self.assertEqual(post.author, self.usr_author)
        response = self.authorized_client_2.get(
            reverse(
                'posts:follow_index',
            )
        )
        post_count = len(response.context['page_obj'])
        self.assertEqual(post_count, 0)
