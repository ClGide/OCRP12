from rest_framework import serializers
from ..CRM import models


class ClientSerializer(serializers.ModelSerializer):

    sales_contact = serializers.SerializerMethodField()

    def get_sales_contact(self, obj):
        sales_contact_name = f"{obj.sales_contact.first_name} {obj.sales_contact.last_name}"
        return sales_contact_name

    class Meta:
        model = models.Client
        fields = ["first_name", "last_name", "email", "phone", "mobile", "company_name", "sales_contact"]
        read_only_fields = ["client_status"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = "__all__"
        # There might be the need to implement the support_contact's constraint here


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contract
        fields = "__all__"
        # There might be the need to implement the sales_contact's constraint here

