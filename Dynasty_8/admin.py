from django.contrib import admin
from Dynasty_8.models import Profile, Rolename, Adver, Apartment, Disrtict, City, Image, Apart_image

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('eEmail', 'phoneNumber', 'roleName')
    list_filter = ('roleName',)
    search_fields = ('eEmail', 'phoneNumber',)

class RolenameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
class DisrtictAdmin(admin.ModelAdmin):
    list_display = ('dictrict_name', 'city_name')
    list_filter = ('city_name',)

class CityAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'region_number')

class ImageAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_path')

class Apart_imageInline(admin.TabularInline):
    model = Apart_image
    extra = 1
    raw_id_fields = ('adver_id', 'image_id')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Rolename, RolenameAdmin)
admin.site.register(Adver)
admin.site.register(Apartment)
admin.site.register(Disrtict, DisrtictAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Image, ImageAdmin)
