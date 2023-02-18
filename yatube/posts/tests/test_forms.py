from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Kurva")
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-descrip'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='old-text',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        url_post_create = reverse(
            'posts:profile',
            kwargs={'username': PostFormTests.user.username}
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test-post',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, url_post_create)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            post.group, PostFormTests.group
        )
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, PostFormTests.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        url_edit_post = reverse(
            'posts:post_edit',
            kwargs={'post_id': PostFormTests.post.pk}
        )
        url_post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': PostFormTests.post.pk}
        )
        form_data = {
            'text': 'old-text',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            url_edit_post,
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=PostFormTests.post.pk)
        self.assertRedirects(response, url_post_detail)
        self.assertEqual(
            post.text,
            form_data['text']
        )
        self.assertEqual(
            post.group.pk,
            form_data['group']
        )

    def test_post_edit_not_create_guest_client(self):
        """Валидная форма не изменит запись в Post если неавторизован."""
        url_edit_post = reverse(
            'posts:post_edit',
            kwargs={'post_id': PostFormTests.post.pk}
        )
        form_data = {
            'text': 'old-text',
            'group': PostFormTests.group.pk,
        }
        response = self.guest_client.post(
            url_edit_post,
            data=form_data,
            follow=True
        )
        login = reverse('login')
        new = url_edit_post
        redirect = login + '?next=' + new
        self.assertRedirects(response, redirect)
        self.assertEqual(response.status_code, HTTPStatus.OK)
