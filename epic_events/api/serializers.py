"""Serializers have two responsibilities. First, converting received JSON data
into Python native data type. Sending the converted data to the views where a first round
of validation takes place. This happens for example when a POST request is received
through the API. Second, converting model instances into JSON data. This happens for
example when a GET request is received through the API."""


from rest_framework import serializers

from ..crm.models import CustomUser, Contract, Event, Client


class CustomUserSerializer(serializers.ModelSerializer):
    """Convert user instances into JSON data and vice versa, if the received data
    is validated."""

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "user_type", "phone"]


class ClientSerializer(serializers.ModelSerializer):
    """Convert client instances into JSON data and vice versa, if the received data
    is validated."""

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "email", "phone",
                  "mobile", "company_name", "sales_contact"]
        read_only_fields = ["client_status"]


class EventSerializer(serializers.ModelSerializer):
    """Convert event instances into JSON data and vice versa, if the received data
    is validated."""

    class Meta:
        model = Event
        fields = "__all__"


class ContractSerializer(serializers.ModelSerializer):
    """Convert contract instances into JSON data and vice versa, if the received data
    is validate."""

    class Meta:
        model = Contract
        fields = "__all__"
