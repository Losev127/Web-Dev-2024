from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from .managers import ActiveAdverManager
from django.urls import reverse
import random
from django.utils.timezone import now

class Review(models.Model):
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE, related_name='reviews', verbose_name="Квартира")
    author = models.CharField(max_length=50, verbose_name="Автор")
    text = models.TextField(verbose_name="Отзыв")
    rating = models.PositiveSmallIntegerField(verbose_name="Рейтинг")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.author} для {self.apartment}"
    
    def clean_rating(self):
        """Проверка, что рейтинг находится в пределах от 1 до 5."""
        if not (1 <= self.rating <= 5):
            raise ValidationError("Рейтинг должен быть в диапазоне от 1 до 5.")
        return self.rating

    
class SocialApp(models.Model):
    sites = models.ManyToManyField(
        Site,
        related_name='dynasty8_socialapps',  # Уникальное имя для обратной связи
        verbose_name="Сайты"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    client_id = models.CharField(max_length=255, verbose_name="ID клиента")
    secret = models.CharField(max_length=255, verbose_name="Секретный ключ")
    provider = models.CharField(max_length=30, verbose_name="Провайдер")

    def __str__(self):
        return self.name

class ProfileManager(models.Manager):
    def admins(self):
        """Возвращает только администраторов."""
        return self.filter(roleName=self.model.RoleChoices.ADMIN)

    def users(self):
        """Возвращает только пользователей."""
        return self.filter(roleName=self.model.RoleChoices.USER)

    def moderators(self):
        """Возвращает только модераторов."""
        return self.filter(roleName=self.model.RoleChoices.MODERATOR)

    def active_profiles(self):
        """Возвращает всех пользователей."""
        return self.all()

class Favorite(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name="Пользователь")
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE, verbose_name="Квартира")
    added_at = models.DateTimeField(default=now, verbose_name="Дата добавления")

    class Meta:
        unique_together = ('profile', 'apartment')  # Уникальная пара
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.profile} добавил {self.apartment} в избранное"
    
class Profile(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'

    id = models.AutoField(primary_key=True)
    adver = models.IntegerField(null=True, blank=True, verbose_name="Количество объявлений")  # Сделано необязательным
    eEmail = models.CharField(max_length=50, blank=False, verbose_name="Email")
    phoneNumber = models.CharField(max_length=20, blank=False, verbose_name="Телефон")
    photo = models.ImageField(
        upload_to='profile_photos/', 
        blank=True, 
        null=True, 
        verbose_name="Фотография профиля"
    )
    contact_link = models.URLField(
        max_length=200, 
        blank=True, 
        verbose_name="Контакт (ссылка)",
        help_text="Введите ссылку на социальные сети или другой контакт"
    )
    roleName = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
        verbose_name="Роль"
    )
    
    # Поле для админки с использованием filter_horizontal
    favorites_simple = models.ManyToManyField('Apartment', related_name='+', blank=True, verbose_name="Избранные квартиры (для админки)")

    favorites = models.ManyToManyField('Apartment', through='Favorite', related_name='favorited_by', verbose_name="Избранные квартиры")

    def save(self, *args, **kwargs):
        """Синхронизируем favorites_simple с промежуточной моделью Favorite при сохранении."""
        super().save(*args, **kwargs)
        self.sync_favorites()

    def sync_favorites(self):
        """Синхронизация временного поля favorites_simple с моделью Favorite."""
        current_favorites = set(Favorite.objects.filter(profile=self).values_list('apartment_id', flat=True))
        new_favorites = set(self.favorites_simple.all().values_list('id', flat=True))

        # Добавляем новые избранные квартиры
        for apartment_id in new_favorites - current_favorites:
            Favorite.objects.create(profile=self, apartment_id=apartment_id)

        # Удаляем удалённые квартиры
        Favorite.objects.filter(profile=self, apartment_id__in=(current_favorites - new_favorites)).delete()

    class Meta:
        verbose_name_plural = "Профили"
        verbose_name = "Профиль"

    def __str__(self):
        return f"{self.eEmail} ({self.get_roleName_display()})"

class Rolename(models.Model):
    name = models.CharField(max_length=20, blank=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = "Статус_пользователя"

class Adver(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _("Есть")
        INACTIVE = 'inactive', _("Нету")

    id = models.AutoField(primary_key=True)
    price = models.IntegerField(blank=False, verbose_name="Цена")
    own = models.CharField(max_length=20, blank=False, verbose_name="Владелец")
    image = models.ImageField(upload_to='adver_images/', blank=False, verbose_name="Фотография")
    mortgage = models.BooleanField(
        default=False,
        verbose_name="Ипотека",
        help_text="Доступна ли ипотека"
    )
    score = models.IntegerField(blank=False, verbose_name="Рейтинг квартиры от риелтора")
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE, related_name='adverts', verbose_name="Квартира")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # История изменений
    history = HistoricalRecords()
    objects = models.Manager()  # Стандартный менеджер
    active_adverts = ActiveAdverManager()  # Кастомный менеджер

    def save(self, *args, **kwargs):
        # Установка случайного значения для рейтинга перед сохранением
        if not self.pk:  # Если объект ещё не сохранён
            self.score = random.randint(1, 10)
        super().save(*args, **kwargs)  # Вызов оригинального метода save()

    class Meta:
        verbose_name_plural = "Объявления"
        verbose_name = _("Объявление")
        ordering = ['price']

    def clean(self):
        # Проверка цены
        if self.price < 1000000:
            raise ValidationError("Цена не может быть ниже 1,000,000.")

    def __str__(self):
        return f"{self.own} ({self.apartment})"


class District(models.Model):
    district_name = models.CharField(max_length=20, blank=False, verbose_name="Название района")
    city_name = models.CharField(max_length=20, blank=False, verbose_name="Город")
    photo = models.ImageField(upload_to='district_photos/', blank=True, null=True, verbose_name="Фотография района")
    infrastructure_rating = models.IntegerField(verbose_name="Рейтинг инфраструктуры", blank=True, help_text="Рейтинг от 1 до 100")
    ecology_rating = models.IntegerField(verbose_name="Экология", blank=True, help_text="Рейтинг от 1 до 100")
    distance_from_center = models.IntegerField(verbose_name="Отдаление от центра", blank=True, help_text="Расстояние в км")
    metro_stations = models.TextField(verbose_name="Станции метро", blank=True, help_text="Введите список станций метро")
    population = models.IntegerField(blank=False, verbose_name="Население", help_text="Введите численность населения")
    construction_years = models.IntegerField(blank=False, verbose_name="Годы застройки", help_text="Введите год застройки")

    class Meta:
        verbose_name_plural = "Районы"
        verbose_name = "Район"

    def __str__(self):
        return f"{self.district_name}, {self.city_name}"
    
    def clean(self):
        if not (1 <= self.infrastructure_rating <= 100):
            raise ValidationError("Рейтинг инфраструктуры должен быть от 1 до 100")
        if not (1 <= self.ecology_rating <= 100):
            raise ValidationError("Рейтинг экологии должен быть от 1 до 100")
        if not (1 <= self.distance_from_center <= 100):
            raise ValidationError("Отдаление от центра должно быть от 1 до 100")
        super().clean()


class Apartment(models.Model):
    floor_app = models.IntegerField(blank=False, verbose_name="Этаж")
    district = models.ForeignKey('District', on_delete=models.CASCADE, related_name='apartments', verbose_name="Район")
    area = models.IntegerField(blank=False, verbose_name="Площадь кв.м.")
    room_quantity = models.IntegerField(blank=False, verbose_name="Кол-во комнат")
    address = models.CharField(max_length=50, blank=False, verbose_name="Адрес")
    description = models.TextField(max_length=100, blank=False, verbose_name="Описание")
    document = models.FileField(upload_to='apartment_documents/', blank=True, null=True, verbose_name="Документ")
    id = models.AutoField(primary_key=True)

    class Meta:
        verbose_name_plural = "Квартиры"
        verbose_name = _("Квартира")

    def clean(self):
        # Проверка, что room_quantity и floor_app — целые числа (уже гарантируется IntegerField)
        if not isinstance(self.room_quantity, int):
            raise ValidationError("Количество комнат должно быть целым числом.")
        if not isinstance(self.floor_app, int):
            raise ValidationError("Этаж должен быть целым числом.")

    def __str__(self):
        return f"Квартира ({self.address})"
    
    def get_absolute_url(self):
        return reverse('apartment_detail', kwargs={'pk': self.pk})

class City(models.Model):
    city_name = models.CharField(max_length=20, blank=False)
    region_number = models.CharField(max_length=20, blank=False)
    class Meta:
        verbose_name_plural = "Город"

class Image(models.Model):
    file_name = models.CharField(max_length=20, blank=False)
    file_path = models.CharField(max_length=20, blank=False)
    url = models.URLField(blank=True, null=True, verbose_name="Ссылка на изображение")
    class Meta:
        verbose_name_plural = "Фото"

class Apart_image(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='images', verbose_name="Квартира")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='apartments', verbose_name="Изображение")

    class Meta:
        verbose_name_plural = "Фото_квартиры"
