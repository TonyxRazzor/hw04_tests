from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        """Стартовая страница."""
        # Создаем клиента
        guest_client = Client()
        # Запрос главной страницы
        response = guest_client.get('/')
        # Код должен быть 200
        self.assertEqual(response.status_code, 200)


class TestPostPage(TestCase):
    @classmethod
    def setUpClass(cls):
        """Вызывается однажды перед запуском всех тестов."""
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(
            username='Kurva'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        """Подготовка прогона теста. Вызывается перед каждым тестом."""
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя(автора)
        self.authorized_client.force_login(self.post.author)

    def tearDown(self):
        """Удаление клиента после тестов."""
        del self.guest_client
        del self.authorized_client

    def check_addr(self, client, templates_list, status_code=None):
        """Запуск подтестов url из словаряю"""
        for reverse_addr, template in templates_list.items():
            response = client.get(reverse_addr)
            err_message = (
                f'адресная строка: {reverse_addr} ; '
                f'ожидается шаблон: {template} ; '
                f'statuscode= {response.status_code}'
            )
            with self.subTest(template=template, response=response):
                if status_code:
                    self.assertEqual(response.status_code, status_code)
                else:
                    self.assertTemplateUsed(response, template, err_message)

    def test_temple_page(self):
        """Контроль корректности url."""
        user_name = self.user.username
        post_id = self.post.id
        slug = self.group.slug
        # Доступ для всех
        templates_list = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': user_name}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': post_id}):
            'posts/post_detail.html',
        }
        self.check_addr(self.guest_client, templates_list)
        # Доступ авторизованным
        templates_list = {
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        self.check_addr(self.authorized_client, templates_list)
        self.check_addr(self.guest_client, templates_list, HTTPStatus.FOUND)
        # Доступ автору
        templates_list = {
            reverse('posts:post_edit', kwargs={'post_id': post_id}):
            'posts/create_post.html',
        }
        self.check_addr(self.authorized_client, templates_list)
        self.check_addr(self.guest_client, templates_list, HTTPStatus.FOUND)
        # 404 not_found
        templ_list = {
            '/unexisting_page/': ' unexisting_page.html'
        }
        self.check_addr(self.guest_client, templ_list, HTTPStatus.NOT_FOUND)
