from django.db.models import QuerySet
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import CustomUserSerializer, ClientSerializer, EventSerializer, ContractSerializer
from epic_events.CRM.models import Client, Event, Contract, CustomUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone


class CustomUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = CustomUser.objects.all()
        if request.user.user_type == 1:
            serializer = CustomUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type in [2, 3]:
            raise PermissionDenied("Only manager can access other users data")


class CreateCustomUserView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomUserSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        if request.user.user_type == 1:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers)
        elif request.user.user_type in [2, 3]:
            raise PermissionDenied("Only manager can create users")


class CustomUserViewSet(GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomUserSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        username = kwargs["username"]
        user = CustomUser.objects.get(username=username)

        if request.user.user_type == 1 or username == request.user.username:
            # if the user is a manager, he has edit access to all users.
            # Moreover, any user can edit his own data.
            serializer = self.serializer_class(user,
                                               data=request.data,
                                               partial=True)
            if request.user.user_type in [2, 3] and request.user.user_type != serializer.initial_data["user_type"]:
                raise PermissionDenied("only managers can change the user_type")
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type in [2, 3]:
            # if the user is in the sales or support team, he has no edit access to other users.
            raise PermissionDenied("Only managers can edit other users data")

    def destroy(self, request, *args, **kwargs):
        """
        Retrieves the requested user, makes sure the user has
        delete authorization and then performs deletion.
        """
        username = kwargs["username"]
        user = CustomUser.objects.get(username=username)

        if request.user.user_type == 1:
            # if the user is in the management team, he can delete any client
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type in [2, 3]:
            raise PermissionDenied("Only managers can delete other users")


class ClientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all clients.
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        for client in serializer.data:
            sales_contact_id = client["sales_contact"]
            if sales_contact_id:
                sales_contact = CustomUser.objects.get(id=sales_contact_id)
                client["sales_contact"] = sales_contact.username
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateClientView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        # only managers and salesmen can add new clients to the CRM.
        if request.user.user_type in [1, 2]:
            if request.user.user_type == 2 and request.user.username != request.data["sales_contact"]:
                raise PermissionDenied("Salesmen cannot assign another salesmen a client")
            serializer = self.get_serializer(data=request.data)
            sales_contact_username = request.data["sales_contact"]
            sales_contact = CustomUser.objects.get(username=sales_contact_username)
            serializer.initial_data["sales_contact"] = sales_contact.id
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
        elif request.user.user_type == 3:
            raise PermissionDenied("only managers and salesmen can add new users to the CRM")
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ClientViewSet(GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        client_last_name = kwargs["last_name"]
        client_first_name = kwargs["first_name"]
        client = Client.objects.get(last_name=client_last_name,
                                    first_name=client_first_name)

        if request.user.user_type in [1, 2]:
            # if the user is a manager, he has edit access to all clients.
            # if the user is a salesmen, he only has edit access to the clients he's
            # assigned to. And he cannot reassign the sales contact.
            salesman_clients = Client.objects.filter(sales_contact_id=request.user.id)
            if request.user.user_type == 2 and client not in salesman_clients:
                raise PermissionDenied("Salesmen can only update his own clients")
            serializer = self.serializer_class(client,
                                               data=request.data,
                                               partial=True)
            sales_contact_username = request.data["sales_contact"]
            sales_contact = CustomUser.objects.get(username=sales_contact_username)
            serializer.initial_data["sales_contact"] = sales_contact.id
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type == 3:
            # if the user is a support team member, he has edit access to no clients.
            raise PermissionDenied

    def destroy(self, request, *args, **kwargs):
        client_first_name = kwargs["first_name"]
        client_last_name = kwargs["last_name"]
        client = Client.objects.get(first_name=client_first_name,
                                    last_name=client_last_name)
        if request.user.user_type in [1, 2]:
            # if the user is in the management team, he can delete any client.
            # if the user is a salesmen, he can only delete his clients
            salesman_clients = Client.objects.filter(sales_contact_id=request.user.id)
            if request.user.user_type == 2 and client not in salesman_clients:
                raise PermissionDenied("Salesmen can only delete their clients")
            client.delete()
        elif request.user.user_type == 3:
            # if the user is in the support team, he can delete no contracts
            raise PermissionDenied("Only managers and salesmen can delete clients")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContractView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all contracts.
        contracts = Contract.objects.all()
        serializer = ContractSerializer(contracts, many=True)
        for contract in serializer.data:
            if contract["sales_contact"]:
                sales_contact = CustomUser.objects.get(id=contract["sales_contact"])
                contract["sales_contract"] = sales_contact.username
            client = Client.objects.get(id=contract["client"])
            contract["client"] = f"{client.first_name} {client.last_name}"
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateContractView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContractSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        if request.user.user_type in [1, 2]:
            serializer = self.get_serializer(data=request.data)
            first_name, last_name = request.data["client"].split(" ")
            client = Client.objects.get(first_name=first_name,
                                        last_name=last_name)
            if request.user.user_type == 2 and client.sales_contact != request.user:
                raise PermissionDenied("Salesmen can create contracts only for their clients")
            serializer.initial_data["client"] = client.id
            sales_contact_username = request.data["sales_contact"]
            sales_contact = CustomUser.objects.get(username=sales_contact_username)
            serializer.initial_data["sales_contact"] = sales_contact.id
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers)
        elif request.user.user_type == 3:
            raise PermissionDenied("Only managers and salesmen can create contracts.")


class ContractViewSet(GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContractSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        contract_title = kwargs["contract_title"]
        contract = Contract.objects.get(title=contract_title)

        if request.user.user_type in [1, 2]:
            # if the user is a manager, he has edit access to all contracts.
            # if the user is a salesmen, he only has edit access to his client's contracts.
            # And he cannot change the sales_contact attribute.
            salesman_clients = Client.objects.filter(sales_contact=request.user.id)
            if request.user.user_type == 2 and contract.client not in salesman_clients:
                raise PermissionDenied("Salesmen can edit only their clients' contracts.")
            serializer = self.serializer_class(contract,
                                               data=request.data,
                                               partial=True)
            username = request.data["sales_contact"]
            sales_contact = CustomUser.objects.get(username=username)
            serializer.initial_data["sales_contact"] = sales_contact.id
            first_name, last_name = request.data["client"].split(" ")
            client = Client.objects.get(first_name=first_name,
                                        last_name=last_name)
            serializer.initial_data["client"] = client.id
            # the title should not contain special ch when inserted in the database. It should
            # only contain alphanumeric values and spaces.
            title_with_underscores = serializer.initial_data["title"]
            title_without_underscores = title_with_underscores.replace("_", " ")
            serializer.initial_data["title"] = title_without_underscores
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type == 3:
            # if the user is a support team member, he cannot edit contracts.
            raise PermissionDenied("Only managers and support team members can edit contracts")

    def destroy(self, request, *args, **kwargs):
        """
        Retrieves the requested contract, makes sure the user has
        delete authorization and then performs deletion.
        """
        contract_title = kwargs["contract_title"]
        contract = Contract.objects.get(title=contract_title)
        if request.user.user_type in [1, 2]:
            # If the user is in the management team, he can delete any contract.
            # if the user is a salesmen, he can only delete his client's contracts.
            salesman_clients = Client.objects.filter(sales_contact=request.user.id)
            if request.user.user_type == 2 and contract.client not in salesman_clients:
                raise PermissionDenied("Salesmen can delete only their clients' contracts.")
            contract.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type == 3:
            # if the user is in the support team member, he cannot delete contracts.
            raise PermissionDenied("Only managers and salesmen can delete contracts.")


class EventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # any authenticated user has read access to all events.
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        for event in serializer.data:
            if event["support_contact"]:
                support_contact_id = event["support_contact"]
                support_contact = CustomUser.objects.get(id=support_contact_id)
                event["support_contact"] = support_contact.username
            contract_id = event["contract"]
            contract = Contract.objects.get(id=contract_id)
            event["contract"] = contract.title
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateEventView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        if request.user.user_type in [1, 2]:
            # Only managers and salesmen can create events.
            # Salesmen can create events only for their clients.
            serializer = self.get_serializer(data=request.data)
            contract_title = request.data["contract"]
            contract = Contract.objects.get(title=contract_title)
            if request.user.user_type == 2 and contract.sales_contact != request.user:
                raise PermissionDenied("Salesmen can only create events for their clients.")
            serializer.initial_data["contract"] = contract.id
            support_contact_username = request.data["support_contact"]
            support_contact = CustomUser.objects.get(username=support_contact_username)
            serializer.initial_data["support_contact"] = support_contact.id
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers)
        elif request.user.user_type == 3:
            raise PermissionDenied("Only managers and salesmen can create events.")


class EventViewSet(GenericViewSet):
    serializer_class = EventSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        event_title = kwargs["event_title"]
        event = Event.objects.get(title=event_title)

        if request.user.user_type in [1, 2]:
            # if the user is a manager, he has edit access to all events.
            if request.user.user_type == 2 and event.contract.sales_contact != request.user:
                # if the user is a salesmen, he only has edit access to his client's events
                raise PermissionDenied("Salesmen can only edit their client's event.")
            serializer = self.serializer_class(event,
                                               data=request.data,
                                               partial=True)
            contract_title = serializer.initial_data["contract"]
            contract = Contract.objects.get(title=contract_title)
            serializer.initial_data["contract"] = contract.id
            support_contact_username = serializer.initial_data["support_contact"]
            support_contact = CustomUser.objects.get(username=support_contact_username)
            serializer.initial_data["support_contact"] = support_contact.id
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type == 3:
            if event.support_contact != request.user:
                # if the user is a support team member, he has edit access to events he's assigned to.
                raise PermissionDenied("Support team members can only edit their events")
            if event.event_date < timezone.now():
                # But he cannot edit his events after they happen.
                raise PermissionDenied("You cannot edit events after they happen")
            serializer = self.serializer_class(event,
                                               data=request.data)
            contract_title = serializer.initial_data["contract"]
            contract = Contract.objects.get(title=contract_title)
            serializer.initial_data["contract"] = contract.id
            support_contact_username = serializer.initial_data["support_contact"]
            support_contact = CustomUser.objects.get(username=support_contact_username)
            serializer.initial_data["support_contact"] = support_contact.id
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

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

