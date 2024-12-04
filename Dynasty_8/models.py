from django.db import models
from django.utils.translation import gettext_lazy as _

class Profile(models.Model):
    adver = models.IntegerField(max_length=20)
    eEmail = models.CharField(max_length=20, blank=False)
    phoneNumber = models.CharField(max_length=20, blank=False)
    roleName = models.CharField(max_length=20, blank=False)
    class Meta:
        verbose_name_plural = "Профиль"

class Rolename(models.Model):
    name = models.CharField(max_length=20, blank=False)
    class Meta:
        verbose_name_plural = "Статус_пользователя"

class Adver(models.Model):
    price = models.IntegerField(max_length=20, blank=False)
    date_created = models.DateField(blank=False)
    own = models.CharField(max_length=20, blank=False)
    image = models.CharField(max_length=20, blank=False)
    mortgage = models.CharField(max_length=20, blank=False)
    score = models.IntegerField(max_length=20, blank=False)
    apartment = models.IntegerField(max_length=20, blank=False)

    class Meta:
        verbose_name_plural = "Объявления"
        verbose_name = _("Объявление")

    def __str__(self):
        return f"Объявление ({self.own})"

  
class Apartment(models.Model):
    floor_app = models.IntegerField(max_length=20, blank=False, verbose_name = "Этаж")
    district = models.CharField(max_length=20, blank=False, verbose_name = "Район")
    area = models.IntegerField(max_length=20, blank=False, verbose_name = "Площадь")
    room_quantity = models.IntegerField(max_length=20, blank=False, verbose_name = "Кол-во комнат")
    address = models.CharField(max_length=20, blank=False, verbose_name = "Адрес")
    description = models.TextField(max_length=100, blank=False, verbose_name = "Описание")

    class Meta:
        verbose_name_plural = "Квартиры"
        verbose_name = _("Квартира")

    def __str__(self):
        return f"Квартира ({self.address})"


class Disrtict(models.Model):
    dictrict_name = models.CharField(max_length=20, blank=False)
    city_name = models.CharField(max_length=20, blank=False)
    class Meta:
        verbose_name_plural = "Район"

class City(models.Model):
    city_name = models.CharField(max_length=20, blank=False)
    region_number = models.CharField(max_length=20, blank=False)
    class Meta:
        verbose_name_plural = "Город"


class Image(models.Model):
    file_name = models.CharField(max_length=20, blank=False)
    file_path = models.CharField(max_length=20, blank=False)
    class Meta:
        verbose_name_plural = "Фото"

class Apart_image(models.Model):
    adver_id = models.CharField(max_length=20, blank=False)
    image_id = models.CharField(max_length=20, blank=False)
    class Meta:
        verbose_name_plural = "Фото_квартиры"
