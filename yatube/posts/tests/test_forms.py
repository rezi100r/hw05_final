import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from django.urls import reverse
from http import HTTPStatus

from ..models import Post, User, Group, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Группа для тестирования 1',
            slug='group-testing-1',
            description='Тестовая группа 1',
        )
        cls.group_2 = Group.objects.create(
            title='Группа для тестирования 2',
            slug='group-testing-2',
            description='Тестовая группа 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=False)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_create_post(self):
        """Валидная форма создает запись."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Статус ответа страницы не соответствует.'
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            msg_prefix='Перенаправление не соответствует ожидаемому'
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        check_post = Post.objects.latest('pk')
        self.assertEqual(check_post.text, form_data['text'])
        self.assertEqual(check_post.author, self.user)
        self.assertEqual(check_post.group, self.group)
        self.assertIn(uploaded.name, check_post.image.name)

    def test_edit_post(self):
        """Валидная форма редактирует запись."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст версия 2',
            'group': self.group_2.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ),
            msg_prefix='Перенаправление не соответствует ожидаемому'
        )
        self.assertEqual(Post.objects.count(), posts_count)
        check_post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(check_post.text, form_data['text'])
        self.assertEqual(check_post.author, self.user)
        self.assertEqual(check_post.group, self.group_2)
        self.assertNotEqual(check_post.group, self.group)
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'group-testing-1'}
            )
        )
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_create_post_guest_client(self):
        """Проверка создания поста не авторизированным клиентом"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст 3',
            'group': self.group.pk
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Статус ответа страницы не соответствует.'
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/',
            msg_prefix='Перенаправление не соответствует ожидаемому'
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_comment_authorized_client(self):
        """Проверка создания комментария авторизированным пользователем"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk},
                    ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ),
            msg_prefix='Перенаправление не соответствует ожидаемому'
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        check_comment = Comment.objects.latest('pk')
        self.assertEqual(check_comment.text, form_data['text'])
        self.assertEqual(check_comment.author, self.user)
        self.assertEqual(
            response.context['comments'][0],
            check_comment
        )

    def test_create_comment_guest_client(self):
        """Проверка создания комментария гостем"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk},
                    ),
            data=form_data,
            follow=True
        )
        page = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        ) + 'comment/'
        self.assertRedirects(
            response,
            '/auth/login/?next=' + page,
            msg_prefix='Перенаправление не соответствует ожидаемому'
        )
        self.assertEqual(Comment.objects.count(), comments_count)
