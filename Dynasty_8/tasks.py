from celery import shared_task
from Dynasty_8.models import Adver
from django.utils.timezone import now
from datetime import timedelta
import random

@shared_task
def delete_old_adverts():
    """
    Удаляет объявления старше 30 дней.
    """
    threshold_date = now() - timedelta(days=30)
    deleted_count, _ = Adver.objects.filter(date_created__lt=threshold_date).delete()
    return f"Удалено {deleted_count} устаревших объявлений"

@shared_task
def update_adver_scores_randomly():
    """
    Обновляет рейтинг объявлений на случайное число от 1 до 10.
    """
    adverts = Adver.objects.all()
    for adver in adverts:
        adver.score = random.randint(1, 10)
        adver.save()
    return f"Обновлено рейтингов для {adverts.count()} объявлений"