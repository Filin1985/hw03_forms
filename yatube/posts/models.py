from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    """Модель группы"""
    title = models.CharField('Имя группы', max_length=200)
    slug = models.SlugField('Идентификатор', unique=True)
    description = models.TextField('Описание группы', max_length=250)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    """Модель поста"""
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Пользователь'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]
