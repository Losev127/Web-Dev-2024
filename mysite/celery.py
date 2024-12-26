from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery import shared_task
from celery import schedules
from celery.schedules import crontab
from celery import Celery

# Установить переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')

# Загрузить настройки Celery из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находить задачи в apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from Dynasty_8.tasks import delete_old_adverts, update_adver_scores_randomly

    # Удаление устаревших объявлений каждые сутки
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        delete_old_adverts.s(),
        name="Удаление устаревших объявлений"
    )

    # Обновление рейтинга каждый 10 минут
    sender.add_periodic_task(
        crontab(minute='*/10'),
        update_adver_scores_randomly.s(),
        name="Обновление рейтинга объявлений"
    )