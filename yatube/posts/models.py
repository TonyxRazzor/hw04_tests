from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):

    def __str__(self) -> str:
        return self.title
    title = models.CharField(
        max_length=200,
        verbose_name='Загаловок группы'
    )
    slug = models.SlugField(
        null=False,
        unique=True
    )
    description = models.TextField(
        verbose_name='Описание группы'
    )

    class Meta:
        verbose_name_plural = 'Группы'


class Post(models.Model):

    def __str__(self):
        return self.text[:15]
    text = models.TextField(
        verbose_name='Загаловок поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относится пост'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Посты'
