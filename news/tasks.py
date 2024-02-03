from celery import shared_task
from django.core.mail import get_connection, EmailMultiAlternatives
from NewsPortal import settings
from django.template.loader import render_to_string
from .models import Post, Category
from django.contrib.auth.models import User
import datetime


@shared_task()
def send_post(post_id):
    instance = Post.objects.get(id=post_id)

    # Создадим цикл, чтобы охватить все категории одного поста
    subscriber_emails = set()
    for post_category in instance.category.all():
        subscribers = post_category.subscribers.all()
        for subscriber in subscribers:
            subscriber_emails.add(subscriber.email)

    messages = list()
    # Через цикл набиваем список сообщений, чтоб они были индивидуальны для каждого пользователя
    for email in subscriber_emails:
        html_content = render_to_string(
            'post_created.html',
            {
                'username': User.objects.get(email=email),
                'post': instance,
                'link': f'{settings.SITE_URL}/news/{instance.id}'
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Новая статья {instance.author} - "{instance.header}"',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html
        messages.append(msg)

    connection = get_connection()  # uses SMTP server specified in settings.py
    connection.send_messages(messages)


@shared_task()
def send_post_digest():
    today = datetime.datetime.now()
    week_ago = today - datetime.timedelta(days=7)
    # посты за неделю
    week_posts = Post.objects.filter(public_date__gte=week_ago)
    # множество категорий, которые были в этих постах
    week_categories = set(week_posts.values_list('category__name', flat=True))
    # чистим от постов без категорий
    week_categories.remove(None)
    # множество имейлов, которые подписаны на эти категории
    emails = set(Category.objects.filter(name__in=week_categories).values_list('subscribers__email', flat=True))
    # чистим от того случая, когда никто не подписан на категорию
    emails.remove(None)

    messages = list()
    # Через цикл набиваем список сообщений, чтоб они были индивидуальны для каждого пользователя
    for email in emails:
        # индивидуальная подборка сообщений для каждого пользователя
        post_list = week_posts.filter(category__subscribers__email=email)
        html_content = render_to_string(
            'post_digest.html',
            {
                'username': User.objects.get(email=email),
                'posts': post_list,
                'link': f'{settings.SITE_URL}'
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Подборка статей за неделю от {datetime.datetime.now().strftime("%d.%m.%Y")}',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html
        messages.append(msg)

    connection = get_connection()  # uses SMTP server specified in settings.py
    connection.send_messages(messages)
