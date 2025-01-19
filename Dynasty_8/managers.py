from django.db import models

class ActiveAdverManager(models.Manager):
    def get_queryset(self):
        """
        Переопределяет стандартный QuerySet, возвращая только активные объявления.
        """
        return super().get_queryset().filter(status='active')

    def with_high_score(self, min_score=8):
        """
        Возвращает объявления с рейтингом выше указанного значения.
        """
        return self.get_queryset().filter(score__gte=min_score)

