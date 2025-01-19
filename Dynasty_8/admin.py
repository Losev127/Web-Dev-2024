from django.contrib import admin
from Dynasty_8.models import Profile, Rolename, Adver, Apartment, District, City, Image, Apart_image, SocialApp, Review, Favorite
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ExportMixin
from import_export import resources
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('profile', 'apartment', 'added_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'author', 'rating', 'created_at')
    search_fields = ('author', 'text')
    list_filter = ('rating', 'created_at')

@admin.register(SocialApp)
class SocialAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider')
    list_filter = ('provider',)
    
class AdverResource(resources.ModelResource):
    class Meta:
        model = Adver
        fields = ('id', 'price', 'date_created', 'own', 'mortgage', 'score', 'apartment', 'full_info')
        export_order = ('id', 'price', 'date_created', 'own', 'mortgage', 'score', 'apartment', 'full_info')

    def get_export_fields(self, resource=None):
        fields = super().get_export_fields(resource)
        custom_headers = {
            'id': 'ID',
            'price': 'Цена',
            'date_created': 'Дата публикации',
            'own': 'Владелец',
            'mortgage': 'Ипотека',
            'score': 'Рейтинг',
            'apartment': 'Квартира',
            'full_info': 'Полная информация'
        }
        for field in fields:
            if field.column_name in custom_headers:
                field.column_name = custom_headers[field.column_name]
        return fields

    # Фильтруем объявления с ипотекой
    def get_export_queryset(self, queryset, **kwargs):
        # Фильтруем только те объявления, где mortgage=True
        return queryset.filter(mortgage=True)

    def dehydrate_price(self, obj):
        return f"{obj.price} ₽"

    def dehydrate_date_created(self, obj):
        return obj.date_created.strftime('%d-%m-%Y')

    def dehydrate_full_info(self, obj):
        return f"Владелец: {obj.own}, Квартира: {obj.apartment.address if obj.apartment else 'Нет'}, Цена: {obj.price} ₽"


class ApartmentResource(resources.ModelResource):
    class Meta:
        model = Apartment
        fields = ('id', 'address', 'district', 'area', 'room_quantity', 'floor_app', 'description', 'full_info')
        export_order = ('id', 'address', 'district', 'area', 'room_quantity', 'floor_app', 'description', 'full_info')

    def get_export_fields(self, resource=None):
        fields = super().get_export_fields(resource)
        custom_headers = {
            'id': 'ID',
            'address': 'Адрес',
            'district': 'Район',
            'area': 'Площадь (кв.м.)',
            'room_quantity': 'Количество комнат',
            'floor_app': 'Этаж',
            'description': 'Описание',
            'full_info': 'Полная информация'
        }
        for field in fields:
            if field.column_name in custom_headers:
                field.column_name = custom_headers[field.column_name]
        return fields
    
    def dehydrate_full_info(self, obj):
        return (
            f"Адрес: {obj.address}, Район: {obj.district.district_name if obj.district else 'Не указан'}, "
            f"Площадь: {obj.area} кв.м., Этаж: {obj.floor_app}"
        )

   
class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 1

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('eEmail', 'phoneNumber', 'roleName', 'contact_link', 'photo_preview')
    list_display_links = ('eEmail',)
    list_filter = ('roleName',)
    search_fields = ('eEmail', 'phoneNumber',)
    filter_horizontal = ('favorites_simple',)

    fieldsets = (
        ("Основная информация", {
            'fields': ('eEmail', 'phoneNumber', 'photo', 'contact_link', 'roleName')
        }),
        ("Избранные квартиры", {
            'fields': ('favorites_simple',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('favorites_simple')

    def photo_preview(self, obj):
        """Отображение миниатюры фотографии в админке."""
        if obj.photo:
            return format_html(f'<img src="{obj.photo.url}" width="50" height="50" style="border-radius: 50%;" />')
        return "Нет фото"
    photo_preview.short_description = "Фотография"

class RolenameAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_length')

    def name_length(self, obj):
        """Возвращает длину названия роли"""
        return len(obj.name)

    name_length.short_description = "Длина названия"

class DistrictAdmin(admin.ModelAdmin):
    list_display = (
        'district_name', 
        'city_name', 
        'infrastructure_rating', 
        'ecology_rating', 
        'distance_from_center', 
        'population'
    )
    list_filter = ('city_name', 'infrastructure_rating', 'ecology_rating')  # Фильтрация по городу и рейтингам
    search_fields = ('district_name', 'city_name', 'metro_stations')  # Поиск по имени района, города и станциям метро
    fieldsets = (
        ("Основная информация", {
            'fields': ('district_name', 'city_name', 'photo')
        }),
        ("Детали района", {
            'fields': (
                'infrastructure_rating', 
                'ecology_rating', 
                'distance_from_center', 
                'metro_stations', 
                'population', 
                'construction_years'
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.infrastructure_rating > 100 or obj.infrastructure_rating < 1:
            obj.infrastructure_rating = 50  # Пример логики обработки некорректных данных
        super().save_model(request, obj, form, change)

class CityAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'formatted_region_number')
    list_filter = ('region_number',)  # Фильтрация по региону
    
    def formatted_region_number(self, obj):
        return f"{obj.region_number}"

    formatted_region_number.short_description = "Номер региона"


class ImageAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_path', 'url')


class Apart_imageInline(admin.TabularInline):
    model = Apart_image
    extra = 1
    raw_id_fields = ('image',)


class AdverInline(admin.TabularInline):
    model = Adver
    fields = ('own', 'price', 'date_created', 'mortgage', 'score', 'apartment_link')
    readonly_fields = ('apartment_link',)
    extra = 0

    def apartment_link(self, obj):
        """
        Форма редактирования связанной квартиры
        """
        if obj.apartment:
            url = reverse("admin:Dynasty_8_apartment_change", args=[obj.apartment.id])
            return format_html('<a href="{}">Редактировать квартиру</a>', url)
        return "Квартира не указана"

    apartment_link.short_description = "Редактировать квартиру"


class ApartmentAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ApartmentResource
    list_display = ('address', 'area','district', 'room_quantity', 'floor_app', 'document', 'get_review_count', 'get_total_apartments')
    list_filter = ('district',)
    search_fields = ('address', 'district__district_name')
    inlines = [Apart_imageInline]
    actions = ['export_as_pdf']  # Добавляем действие в список действий

    @admin.display(description="Количество отзывов")
    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_queryset(self, request):
        # Оптимизация запросов с использованием select_related и prefetch_related
        queryset = super().get_queryset(request)
        return queryset.select_related('district').prefetch_related('reviews').order_by('area')

    fieldsets = (
        ('Основная информация', {
            'fields': ('address', 'district')
        }),
        ('Детали', {
            'fields': ('area', 'room_quantity', 'floor_app', 'description', 'document')
        }),
    )

    def get_total_apartments(self, obj):
        return Apartment.objects.count()

    get_total_apartments.short_description = "Всего квартир"

    def export_as_pdf(self, request, queryset):
        """Генерирует PDF с выбранными квартирами с поддержкой кириллицы."""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="apartments.pdf"'

        # Создаем объект canvas для PDF
        pdf = canvas.Canvas(response, pagesize=A4)

        # Подключаем шрифт с поддержкой кириллицы
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdf.setFont("DejaVuSans", 12)

        # Задаем начальные координаты
        x = 50
        y = 800
        line_height = 20

        # Заголовок PDF документа
        pdf.drawString(x, y, "Список выбранных квартир")
        y -= line_height

        # Генерация строк для каждой квартиры
        for apartment in queryset:
            pdf.drawString(x, y, f"Адрес: {apartment.address}")
            y -= line_height
            pdf.drawString(x, y, f"Район: {apartment.district.district_name if apartment.district else 'Не указан'}")
            y -= line_height
            pdf.drawString(x, y, f"Площадь: {apartment.area} кв.м.")
            y -= line_height
            pdf.drawString(x, y, f"Этаж: {apartment.floor_app}")
            y -= line_height
            pdf.drawString(x, y, f"Описание: {apartment.description}")
            y -= 2 * line_height

            # Если текст выходит за пределы страницы, создаем новую страницу
            if y < 100:
                pdf.showPage()
                pdf.setFont("DejaVuSans", 12)
                y = 800

        pdf.save()  # Сохраняем PDF

        return response
    
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }


class AdverAdmin(ExportMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    resource_class = AdverResource
    list_display = ('own', 'price', 'date_created', 'apartment', 'mortgage', 'score')
    list_filter = ('date_created',)  # Фильтрация по дате публикации
    search_fields = ('own', 'apartment__address')  # Поиск по владельцу и адресу квартиры

    actions = ['export_mortgage_ads']

    def export_mortgage_ads(self, request, queryset):
        resource = self.resource_class()
        queryset = resource.get_export_queryset(queryset, filter_mortgage=True)
        dataset = resource.export(queryset)

        # Используем формат `xlsx` для экспорта
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="adverts_with_mortgage.xlsx"'
        return response

    export_mortgage_ads.short_description = "Экспортировать объявления с ипотекой"



admin.site.register(Profile, ProfileAdmin)
admin.site.register(Rolename, RolenameAdmin)
admin.site.register(Adver, AdverAdmin)
admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Image, ImageAdmin)
