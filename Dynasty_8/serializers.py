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

    def validate_price(self, value):
        if value < 1000000:
            raise serializers.ValidationError("Цена не может быть ниже 1,000,000.")
        return value
