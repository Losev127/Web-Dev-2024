from rest_framework import serializers
from .models import Adver, Apartment, District, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class ApartmentSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()  # Вложенный сериализатор для района

    class Meta:
        model = Apartment
        fields = '__all__'

    # Создание нового объекта
    def create(self, validated_data):
        # Извлечение данных для района
        district_data = validated_data.pop('district', None)
        if district_data:
            district, created = District.objects.get_or_create(**district_data)
            validated_data['district'] = district
        
        # Создаем объект Apartment
        return Apartment.objects.create(**validated_data)

    # Обновление существующего объекта
    def update(self, instance, validated_data):
        # Извлечение и обновление данных для района
        district_data = validated_data.pop('district', None)
        if district_data:
            district, created = District.objects.get_or_create(**district_data)
            instance.district = district

        # Обновление остальных полей
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    # Валидации
    def validate_room_quantity(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("Количество комнат должно быть целым числом.")
        return value

    def validate_floor_app(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("Этаж должен быть целым числом.")
        return value


class AdverSerializer(serializers.ModelSerializer):
    apartment = ApartmentSerializer()  # Вложенный сериализатор для квартиры

    class Meta:
        model = Adver
        fields = '__all__'

    # Создание нового объекта
    def create(self, validated_data):
        # Извлечение данных для квартиры
        apartment_data = validated_data.pop('apartment', None)
        if apartment_data:
            district_data = apartment_data.pop('district', None)
            if district_data:
                district, created = District.objects.get_or_create(**district_data)
                apartment_data['district'] = district
            
            apartment, created = Apartment.objects.get_or_create(**apartment_data)
            validated_data['apartment'] = apartment

        # Создаем объект Adver
        return Adver.objects.create(**validated_data)

    # Обновление существующего объекта
    def update(self, instance, validated_data):
        # Извлечение и обновление данных для квартиры
        apartment_data = validated_data.pop('apartment', None)
        if apartment_data:
            district_data = apartment_data.pop('district', None)
            if district_data:
                district, created = District.objects.get_or_create(**district_data)
                apartment_data['district'] = district
            
            apartment, created = Apartment.objects.get_or_create(**apartment_data)
            instance.apartment = apartment

        # Обновление остальных полей
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    # Валидация
    def validate_price(self, value):
        if value < 1000000:
            raise serializers.ValidationError("Цена не может быть ниже 1,000,000.")
        return value
