from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    adver = models.IntegerField()
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
    class Status(models.TextChoices):
        ACTIVE = 'active', _("Есть")
        INACTIVE = 'inactive', _("Нету")

    id = models.AutoField(primary_key=True)
    price = models.IntegerField(blank=False, verbose_name="Цена")
    date_created = models.DateField(blank=False, verbose_name="Дата публикации")
    own = models.CharField(max_length=20, blank=False, verbose_name="Владелец")
    image = models.CharField(max_length=20, blank=False, verbose_name="Фотография")
    mortgage = models.BooleanField(
        default=False,
        verbose_name="Ипотека",
        help_text="Доступна ли ипотека"
    )
    score = models.IntegerField(blank=False, verbose_name="Рейтинг квартиры от риелтора")
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE, related_name='adverts', verbose_name="Квартира")

    class Meta:
        verbose_name_plural = "Объявления"
        verbose_name = _("Объявление")

class District(models.Model):
    district_name = models.CharField(max_length=20, blank=False, verbose_name="Название района")
    city_name = models.CharField(max_length=20, blank=False, verbose_name="Город")

    class Meta:
        verbose_name_plural = "Районы"
        verbose_name = "Район"

    def __str__(self):
        return f"{self.district_name}, {self.city_name}"

class Apartment(models.Model):
    floor_app = models.IntegerField(blank=False, verbose_name="Этаж")
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='apartments', verbose_name="Район")
    area = models.IntegerField(blank=False, verbose_name="Площадь")
    room_quantity = models.IntegerField(blank=False, verbose_name="Кол-во комнат")
    address = models.CharField(max_length=50, blank=False, verbose_name="Адрес")
    description = models.TextField(max_length=100, blank=False, verbose_name="Описание")
    id = models.AutoField(primary_key=True)

    class Meta:
        verbose_name_plural = "Квартиры"
        verbose_name = _("Квартира")

    def __str__(self):
        return f"Квартира ({self.address})"

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
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='images', verbose_name="Квартира")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='apartments', verbose_name="Изображение")

    class Meta:
        verbose_name_plural = "Фото_квартиры"

