from django.db.models import QuerySet
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import ClientSerializer, EventSerializer, ContractSerializer
from epic_events.CRM.models import Client, Event, Contract, CustomUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import PermissionDenied


class ClientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all clients.
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateClientView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        sales_contact_username = request.data["sales_contact"]
        sales_contact = CustomUser.objects.get(username=sales_contact_username)
        serializer.initial_data["sales_contact"] = sales_contact.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ClientViewSet(GenericViewSet):
    serializer_class = ClientSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        client_last_name = kwargs["last_name"]
        client_first_name = kwargs["first_name"]
        client = Client.objects.get(last_name=client_last_name,
                                    first_name=client_first_name)

        if request.user.user_type == 1:
            # if the user is a manager, he has edit access to all clients.
            serializer = self.serializer_class(client,
                                               data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type == 2:
            # if the user is a salesmen, he only has edit access to the clients he's
            # assigned to.
            salesman_clients = Client.objects.filter(sales_contact_id=request.user.id)
            if client in salesman_clients:
                serializer = self.serializer_class(client,
                                                   data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return PermissionDenied
        elif request.user.user_type == 3:
            # if the user is a support team member, he has edit access to no clients.
            return PermissionDenied

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        Retrieves the requested client, makes sure the user has
        delete authorization and then performs deletion.
        """
        client_last_name = kwargs["last_name"]
        client_first_name = kwargs["first_name"]
        client = Client.objects.get(last_name=client_last_name,
                                    first_name=client_first_name)
        if request.user.user_type == 1:
            # if the user is in the management team, he can delete any client
            client.delete()
        elif request.user.user_type == 2:
            # if the user is a salesmen, he can only delete his client's
            salesman_clients = Client.objects.filter(sales_contact_id=request.user.id)
            if client in salesman_clients:
                client.delete()
        elif request.user.user_type == 3:
            # if the user is in the support team, he can delete no contracts
            return PermissionDenied
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContractView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all contracts.
        contracts = Contract.objects.all()
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateContractView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContractSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ContractViewSet(GenericViewSet):
    serializer_class = ContractSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        contract_title = kwargs["contract_title"]
        contract = Contract.objects.get(title=contract_title)

        if request.user.user_type == 1:
            # if the user is a manager, he has edit access to all contracts.
            serializer = self.serializer_class(contract,
                                               data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type == 2:
            # if the user is a salesmen, he only has edit access to his client's contracts
            salesman_clients = Client.objects.filter(sales_contact=request.user.id)
            if contract.client in salesman_clients:
                serializer = self.serializer_class(contract,
                                                   data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return PermissionDenied
        elif request.user.user_type == 3:
            # if the user is a support team member, he has edit access to no contracts
            return PermissionDenied

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        Retrieves the requested contract, makes sure the user has
        delete authorization and then performs deletion.
        """
        contract_title = kwargs["contract_title"]
        contract = Contract.objects.get(title=contract_title)
        if request.user.user_type == 1:
            # If the user is in the management team, he can delete any contract.
            contract.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type == 2:
            # if the user is a salesmen, he can only delete his client's contracts.
            salesman_clients = Client.objects.filter(sales_contact=request.user.id)
            if contract.client in salesman_clients:
                contract.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return PermissionDenied
        elif request.user.user_type == 3:
            # if the user is in the support team member, he cannot delete contracts.
            return PermissionDenied


class EventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all events.
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateEventView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class EventViewSet(GenericViewSet):
    serializer_class = EventSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        event_title = kwargs["event_title"]
        event = Event.objects.get(title=event_title)

        if request.user.user_type == 1:
            # if the user is a manager, he has edit access to all events.
            serializer = self.serializer_class(event,
                                               data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type == 2:
            # if the user is a salesmen, he only has edit access to his client's events
            salesman_clients = Client.objects.filter(sales_contact=request.user.id)
            client_event = event.contract.client
            if client_event in salesman_clients:
                serializer = self.serializer_class(event,
                                                   data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return PermissionDenied
        elif request.user.user_type == 3:
            # if the user is a support team member, he has edit access to events he's assigned to.
            if event.support_contact == request.user.id:
                serializer = self.serializer_class(event,
                                                   data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return PermissionDenied

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        Retrieves the requested event, makes sure the user has
        delete authorization and then performs deletion.
        """
        event_title = kwargs["event_title"]
        event = Event.objects.get(title=event_title)
        if request.user.user_type == 1:
            # If the user is in the management team, he can delete any event.
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type == 2:
            # if the user is a salesmen, he can only delete his client's events.
            salesman_clients = Client.objects.filter(sales_contact=request.user.id)
            client_event = event.contract.client
            if client_event in salesman_clients:
                event.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return PermissionDenied
        elif request.user.user_type == 3:
            # if the user is in the support team member, he cannot delete events.
            return PermissionDenied




