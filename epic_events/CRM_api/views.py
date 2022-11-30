from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import ClientSerializer, EventSerializer, ContractSerializer
from epic_events.CRM.models import Client, Event, Contract
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import GenericViewSet


class CreateClientView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ClientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all clients.
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContractView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all contracts.
        contracts = Contract.objects.all()
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all events.
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ClientViewSet(GenericViewSet):
    serializer_class = ClientSerializer
    http_method_names = ["get", "post", "put", "delete"]

    def update(self, request, *args, **kwargs):
        if request.user.user_type == 1:
            # if the user is a manager, he has access to all users.
            clients = Client.objects.all()
            serializer = ClientSerializer(clients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type == 2:
            # if the user is a salesmen, he only has access to the clients he's
            # assigned to.
            clients = Client.objects.filter(sales_contact_id=request.user.id)
            serializer = ClientSerializer(clients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # if the user is a support team member, he doesn'
            # some permission denial
            return