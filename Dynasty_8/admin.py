from django.contrib import admin
from Dynasty_8.models import Profile, Rolename, Adver, Apartment, District, City, Image, Apart_image
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ExportMixin
from import_export import resources
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse


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


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('eEmail', 'phoneNumber', 'roleName')
    list_filter = ('roleName',)  # Фильтрация по статусу
    search_fields = ('eEmail', 'phoneNumber',) 


class RolenameAdmin(admin.ModelAdmin):
    list_display = ('name',)


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('district_name', 'city_name')
    list_filter = ('city_name',)  # Фильтрация по городу


class CityAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'formatted_region_number')
    list_filter = ('region_number',)  # Фильтрация по региону
    
    def formatted_region_number(self, obj):
        return f"{obj.region_number}"

    formatted_region_number.short_description = "Номер региона"


class ImageAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_path')


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
    list_display = ('address', 'district', 'area', 'room_quantity', 'floor_app')
    list_filter = ('district',)
    inlines = [Apart_imageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('address', 'district')
        }),
        ('Детали', {
            'fields': ('area', 'room_quantity', 'floor_app', 'description')
        }),
    )


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
