from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='Описание')

    def test_create_post(self):
        """Проверка создания поста"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        error_name1 = 'Данные поста не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        text='Текст записанный в форму',
                        group=self.group.id,
                        author=self.user
                        ).exists(), error_name1)
        error_name2 = 'Поcт не добавлен в базу данных'
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         error_name2)

    def test_reddirect_guest_client(self):
        """Проверка редиректа неавторизованного пользователя"""
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        form_data = {'text': 'Текст записанный в форму'}
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_can_edit_post(self):
        """Проверка прав редактирования"""
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        old_text = self.post
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        group=self.group.id,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists(), 'Данные поста не совпадают')
        self.assertNotEqual(
            old_text.text,
            form_data['text'],
            'Пользователь не может изменить содержание поста'
        )
        self.assertNotEqual(
            old_text.group,
            form_data['group'],
            'Пользователь не может изменить группу поста'
        )
