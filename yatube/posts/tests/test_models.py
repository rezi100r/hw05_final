from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись проверки 15 символов',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_str_view = {
            self.group.title: self.group,
            self.post.text[:15]: self.post,
        }
        for expected, value in models_str_view.items():
            with self.subTest(value=value):
                self.assertEqual(
                    expected,
                    str(value),
                    'У моделей Post или Group не корректно работает __str__'
                )

    def test_help_text_post(self):
        """help_text Post в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Напишите текст поста',
            'group': 'Выберите группу',
            'image': 'Добавьте картинку',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text,
                    expected,
                    'help_text модели Post не совпадает с ожидаемыми.'
                )

    def test_help_text_group(self):
        """help_text Group в полях совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'Дайте название группе',
            'slug': ('Укажите адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Укажите описание группы.',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.group._meta.get_field(value).help_text,
                    expected,
                    'help_text модели Group не совпадает с ожидаемыми.'
                )

    def test_verbose_name_post(self):
        """verbose_name Post в полях совпадает с ожидаемым."""
        field_verbose_name = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name,
                    expected,
                    'verbose_name модели Post не совпадает с ожидаемыми.'
                )

    def test_verbose_name_group(self):
        """verbose_name Group в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verbose_name = {
            'title': 'Название',
            'slug': 'Адрес для страницы группы',
            'description': 'Описание группы',
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name,
                    expected,
                    'verbose_name модели Group не совпадает с ожидаемыми.'
                )
