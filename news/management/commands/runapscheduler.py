import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

import datetime
from news.models import Post, Category
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection

logger = logging.getLogger(__name__)


def my_job():
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



# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week='Tue', hour='22', minute='59'),  # Every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")