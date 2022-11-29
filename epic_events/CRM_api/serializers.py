from rest_framework import serializers
from ..CRM import models


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ["__all__"]


