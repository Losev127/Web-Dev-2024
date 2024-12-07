from django.contrib import admin
from Dynasty_8.models import Profile, Rolename, Adver, Apartment, District, City, Image, Apart_image


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
    list_display = ('city_name', 'region_number')
    list_filter = ('region_number',)  # Фильтрация по региону


class ImageAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_path')


class Apart_imageInline(admin.TabularInline):
    model = Apart_image
    extra = 1
    raw_id_fields = ('image',)


class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('address', 'district', 'area', 'room_quantity', 'floor_app')
    inlines = [Apart_imageInline]
    list_filter = ('district',)  # Фильтрация по району


class AdverAdmin(admin.ModelAdmin):
    list_display = ('own', 'price', 'date_created', 'apartment', 'mortgage', 'score')
    list_filter = ('date_created',)  # Фильтрация по дате публикации
    search_fields = ('own', 'apartment__address')  # Поиск по владельцу и адресу квартиры


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Rolename, RolenameAdmin)
admin.site.register(Adver, AdverAdmin)  # Используем AdverAdmin
admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Image, ImageAdmin)
