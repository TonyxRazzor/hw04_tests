from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Group

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='yKurva')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-text'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-text',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTest.user)

    def test_page_uses_correct_template(self):
        """Проверка шаблонов."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': PostPagesTest.user}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


COUNT_OF_POST = 13


class PaginatorViewsTest(TestCase):
    """Пагинатор настройка."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Kurva')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-text'
        )
        posts = list()
        for i in range(COUNT_OF_POST):
            posts.append(Post(text=f'Text number {i}',
                              group=cls.group,
                              author=cls.user))
        Post.objects.bulk_create(posts)[10]
        cls.templates_pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Kurva'}):
            'posts/profile.html',
        }

    def test_first_page_contains_ten_records(self):
        """Пагинатор 10 записей."""
        for reverse_name in self.templates_pages.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Пагинатор 3 записи."""
        for reverse_name in self.templates_pages.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get((reverse_name) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
