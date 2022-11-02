from rest_framework import serializers

from .models import Kardex

class KardexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kardex
        fields = ('__all__')
