import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')

app = Celery('news')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_digest_friday_16pm': {
        'task': 'news.tasks.send_post_digest',
        'schedule': crontab(hour=16, minute=0, day_of_week='friday'),
        # 'args': (),
    },
}
