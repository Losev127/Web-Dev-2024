from django.core.mail import send_mail
from django.core.cache import cache
from Dynasty_8.models import Adver

def send_test_email():
    subject = "Тестовое письмо от Django"
    message = "Это тестовое письмо, отправленное через MailHog."
    from_email = "test@example.com"
    recipient_list = ["recipient@example.com"]

    send_mail(subject, message, from_email, recipient_list)

def get_adverts_by_apartment(apartment_id):
    """
    Извлекает объявления по ID квартиры из кэша или базы данных.
    """
    cache_key = f"adverts_apartment_{apartment_id}"
    adverts = cache.get(cache_key)

    if adverts is None:
        adverts = list(Adver.objects.filter(apartment_id=apartment_id))
        cache.set(cache_key, adverts, timeout=60 * 15)  # Кэш на 15 минут

    return adverts
