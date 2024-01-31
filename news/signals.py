from django.contrib.auth.models import User
from django.core.mail import get_connection, EmailMultiAlternatives
from  django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from NewsPortal import settings
from news.models import PostCategory


@receiver(m2m_changed, sender=PostCategory)
def new_post_notification(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
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