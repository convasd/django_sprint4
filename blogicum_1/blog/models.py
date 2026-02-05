from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AbstractPublishableModel(models.Model):
    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
        blank=False
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True,
        blank=False)

    class Meta:
        abstract = True


class Category(AbstractPublishableModel):
    title = models.CharField(
        verbose_name='Заголовок', max_length=settings.LENGTH_256)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=settings.LENGTH_64,
        unique=True,
        help_text=('Идентификатор страницы для URL; разрешены'
                   ' символы латиницы, цифры, дефис и подчёркивание.'),
        blank=False)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:settings.LENGTH_15]


class Location(AbstractPublishableModel):
    name = models.CharField(
        verbose_name='Название места',
        max_length=settings.LENGTH_256,
        blank=False)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(AbstractPublishableModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=settings.LENGTH_256,
        blank=False)
    image = models.ImageField('Фото', upload_to='post_images', blank=True)
    text = models.TextField(
        verbose_name='Текст',
        blank=False)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время в будущем —'
                   ' можно делать отложенные публикации.'),
        blank=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        blank=False)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Местоположение',
        blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория',
        blank=False)

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title[:settings.LENGTH_15]


class Comment(models.Model):
    text = models.TextField('Комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Пост'
        )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
        )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:settings.LENGTH_256]
