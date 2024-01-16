from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy


# Модель автор - один к одному с пользователем
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def update_rating(self):
        self.rating = (Post.objects.filter(author=self).aggregate(Sum('rating'))['rating__sum'] * 3
                       + Comment.objects.filter(user__author=self).aggregate(Sum('rating'))['rating__sum']
                       + Comment.objects.filter(post__author=self).aggregate(Sum('rating'))['rating__sum'])
        self.save()


# Уникальная категория публикации
class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


# Заготовка списка кортежей под выбор типа публикации в модели Post
post = 'post'
news = 'news'
post_types = [(post, 'Статья'), (news, 'Новость')]


# Собственно модель публикации
class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=10, choices=post_types, default=post)
    public_date = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    header = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        if len(str(self.content)) > 125:
            return self.content[:124] + '...'
        else:
            return self.content

    def __str__(self):
        return f'{self.header}: {self.preview()}'

    def get_absolute_url(self):
        if self.post_type == post:
            return reverse('article_detail', args=[str(self.id)])
        elif self.post_type == news:
            return reverse('news_detail', args=[str(self.id)])
        else:
            reverse_lazy('post_list')


# Промежуточная таблица для организации связи многие ко многим между публикациями и категориями
class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


# Модель комментария под постом
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    public_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
