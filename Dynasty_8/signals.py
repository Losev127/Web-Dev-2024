from functools import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from Dynasty_8.models import Adver

@receiver(post_save, sender=Adver)
@receiver(post_delete, sender=Adver)
def clear_adver_cache(sender, instance, **kwargs):
    """
    Очищает кэш объявлений при изменении или удалении объекта.
    """
    cache_key = f"adverts_apartment_{instance.apartment.id}"
    cache.delete(cache_key)