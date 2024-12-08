from django.contrib import admin
from Dynasty_8.models import Profile, Rolename, Adver, Apartment, District, City, Image, Apart_image
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ExportMixin
from import_export import resources
from django.utils.html import format_html
from django.urls import reverse

class AdverResource(resources.ModelResource):
    class Meta:
        model = Adver
        fields = ('id', 'price', 'date_created', 'own', 'mortgage', 'score', 'apartment')
        export_order = ('id', 'price', 'date_created', 'own', 'mortgage', 'score', 'apartment')

    # Метод для фильтрации набора данных при экспорте
    def get_export_queryset(self, queryset, **kwargs):
        # Возвращаем только активные объявления
        return queryset.filter(mortgage=True)

    # Метод для изменения формата поля `price`
    def dehydrate_price(self, adver):
        # Преобразуем цену в строку с валютой
        return f"{adver.price} ₽"

    # Метод для добавления вычисляемого поля
    def get_full_info(self, adver):
        # Возвращаем строку с полной информацией об объекте
        return f"{adver.own} - {adver.apartment} (Рейтинг: {adver.score})"

class ApartmentResource(resources.ModelResource):
    class Meta:
        model = Apartment
        fields = ('id', 'address', 'district', 'area', 'room_quantity', 'floor_app', 'description')
        export_order = ('id', 'address', 'district', 'area', 'room_quantity', 'floor_app', 'description')

    # Метод для фильтрации набора данных при экспорте
    def get_export_queryset(self, queryset, **kwargs):
        # Возвращаем только квартиры с площадью больше 50 кв.м.
        return queryset.filter(area__gt=50)

    # Метод для изменения формата поля `area` (площадь)
    def dehydrate_area(self, apartment):
        # Добавляем "кв.м." к значению площади
        return f"{apartment.area} кв.м."

    # Метод для добавления вычисляемого поля
    def get_full_info(self, apartment):
        # Возвращаем строку с полной информацией о квартире
        return (
            f"Адрес: {apartment.address}, Район: {apartment.district}, "
            f"Площадь: {apartment.area} кв.м., Этаж: {apartment.floor_app}"
        )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('eEmail', 'phoneNumber', 'roleName')
    list_filter = ('roleName',) # Фильтрация по статусу
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
    fields = ('own', 'price', 'date_created', 'mortgage', 'score', 'adver_link')
    readonly_fields = ('adver_link',)
    extra = 0

    def adver_link(self, obj):
        if obj.id:
            url = reverse("admin:Dynasty_8_adver_change", args=[obj.id])
            return format_html('<a href="{}">Перейти к объявлению</a>', url)
        return "Нет объявления"

    adver_link.short_description = "Ссылка на объявление"


class ApartmentAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ApartmentResource
    list_display = ('address', 'district', 'area', 'room_quantity', 'floor_app')
    inlines = [Apart_imageInline, AdverInline]
    list_filter = ('district',)



class AdverAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AdverResource
    list_display = ('own', 'price', 'date_created', 'apartment', 'mortgage', 'score')
    list_filter = ('date_created',)  # Фильтрация по дате публикации
    search_fields = ('own', 'apartment__address')  # Поиск по владельцу и адресу квартиры

class AdverAdmin(SimpleHistoryAdmin):
    list_display = ('own', 'price', 'date_created', 'apartment', 'mortgage', 'score')
    list_filter = ('date_created',)
    search_fields = ('own', 'apartment__address')

def apartment_link(self, obj):
    url = reverse("admin:yourapp_apartment_change", args=[obj.apartment.id])
    return format_html('<a href="{}">{}</a>', url, obj.apartment.address)
apartment_link.short_description = "Квартира"  # Название колонки


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Rolename, RolenameAdmin)
admin.site.register(Adver, AdverAdmin)
admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Image, ImageAdmin)
