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

class AdverSerializer(serializers.ModelSerializer):
    apartment = ApartmentSerializer()  # Вложенный сериализатор для квартиры

    class Meta:
        model = Adver
        fields = '__all__'
