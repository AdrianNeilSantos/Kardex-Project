from rest_framework import serializers

from .models import Kardex, Nurse

class KardexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kardex
        fields = ('__all__')

class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'sex',
            'ward',
            'department',
            'picture'
        )
