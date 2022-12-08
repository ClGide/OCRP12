"""For each of the four models defined in CRM/models.py the module defines three views.

One view is responsible for the GET request, a second one for the POST request
and a third one for both the PUT and DELETE request. In other words, this module
ensures that for each model the CRUD operations are available through the API."""


from django.utils import timezone
from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from epic_events.CRM.models import Client, Event, Contract, CustomUser
from .serializers import CustomUserSerializer, ClientSerializer, EventSerializer, ContractSerializer


class CustomUserView(APIView):
    """The get method ensures an authenticated user can access the CustomUser model according to his
    permissions."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Only managers have read access to other User instances. Salesmen and Support team
        members can access other Users."""
        users = CustomUser.objects.all()
        if request.user.user_type == 1:
            serializer = CustomUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type in [2, 3]:
            user = CustomUserSerializer(request.user)
            return Response(user.data, status=status.HTTP_200_OK)


class CreateCustomUserView(CreateAPIView):
    """The create method ensures an authenticated user can create a User instance according to his
    permissions."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomUserSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        """Only managers can create new Client instances."""
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
    """The update method ensures an authenticated user can update a User instance according to his
    permissions. The destroy method ensures an authenticated user can delete a User instance
    according to his permissions."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomUserSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        """Only managers can modify other User instances. Salesman and support team members
        can modify their own User instance. However, they cannot change their user_type field."""
        username = kwargs["username"]
        user = CustomUser.objects.get(username=username)

        if request.user.user_type == 1 or username == request.user.username:
            # if the user is a manager, he has edit access to all users.
            # Moreover, any user can edit his own data.
            serializer = self.serializer_class(user,
                                               data=request.data,
                                               partial=True)
            if (request.user.user_type in [2, 3]
                    and request.user.user_type != serializer.initial_data["user_type"]):
                raise PermissionDenied("only managers can change the user_type")
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.user_type in [2, 3]:
            # if the user is in the sales or support team, he has no edit access to other users.
            raise PermissionDenied("Only managers can edit other users data")

    def destroy(self, request, *args, **kwargs):
        """Only managers can delete User instances."""
        username = kwargs["username"]
        user = CustomUser.objects.get(username=username)

        if request.user.user_type == 1:
            # if the user is in the management team, he can delete any client
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type in [2, 3]:
            raise PermissionDenied("Only managers can delete users")


class ClientView(APIView):
    """The get method ensures an authenticated user can access the Client model according to his
    permissions."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Any authenticated user has read access to all clients."""
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        for client in serializer.data:
            sales_contact_id = client["sales_contact"]
            if sales_contact_id:
                sales_contact = CustomUser.objects.get(id=sales_contact_id)
                client["sales_contact"] = sales_contact.username
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateClientView(CreateAPIView):
    """The create method ensures an authenticated user can create a Client instance according to his
    permissions"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        """Only managers and salesmen can add new clients to the CRM. Salesmen can edit only their
        clients."""
        if request.user.user_type in [1, 2]:
            if request.user.user_type == 2 and request.user.username != request.data["sales_contact"]:
                raise PermissionDenied("Salesmen cannot assign another salesmen a client")
            serializer = self.get_serializer(data=request.data)
            # Foreign key relationships are done through pk, in our case the id. However, that
            # pk shouldn't be public. Thus, we use the username field to access the CustomUser
            # related model.
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
    """The update method ensures an authenticated user can update a Client instance according to his
    permissions. The destroy method ensures an authenticated user can delete a Client instance
    according to his permissions.

    By default, queries are made through pk, in our case the id. However, that
    pk shouldn't be public. Thus, we use the first name and last name fields to query
    the client that's going to be modified/deleted.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        """If the user is a manager, he has edit access to all clients.
        If the user is a salesmen, he only has edit access to the clients he's
        assigned to. And he cannot change the sales_contact field. Support team
        members cannot modify Client instances.
        """
        client_last_name = kwargs["last_name"]
        client_first_name = kwargs["first_name"]
        client = Client.objects.get(last_name=client_last_name,
                                    first_name=client_first_name)
        if request.user.user_type in [1, 2]:
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
            raise PermissionDenied

    def destroy(self, request, *args, **kwargs):
        """If the user is in the management team, he can delete any client.
        If the user is a salesmen, he can only delete his clients. Support team members
        cannot delete contacts.
        """
        client_first_name = kwargs["first_name"]
        client_last_name = kwargs["last_name"]
        client = Client.objects.get(first_name=client_first_name,
                                    last_name=client_last_name)
        if request.user.user_type in [1, 2]:
            salesman_clients = Client.objects.filter(sales_contact_id=request.user.id)
            if request.user.user_type == 2 and client not in salesman_clients:
                raise PermissionDenied("Salesmen can only delete their clients")
            client.delete()
        elif request.user.user_type == 3:
            raise PermissionDenied("Only managers and salesmen can delete clients")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContractView(APIView):
    """The get method ensures an authenticated user can access the Contract model according to his
    permissions."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Any authenticated user has read access to all contracts.

        Foreign key relationships are done through pk, in our case the id. However, that
        pk shouldn't be public. Thus, we use the username field to represent the CustomUser
        related model.
        """
        contracts = Contract.objects.all()
        serializer = ContractSerializer(contracts, many=True)
        for contract in serializer.data:
            if contract["sales_contact"]:
                sales_contact = CustomUser.objects.get(id=contract["sales_contact"])
                contract["sales_contact"] = sales_contact.username
            client = Client.objects.get(id=contract["client"])
            contract["client"] = f"{client.first_name} {client.last_name}"
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateContractView(CreateAPIView):
    """The create method ensures an authenticated user can create a Contract instance according to his
    permissions"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContractSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        """Managers can create contracts for any clients. Salesmen can only create contracts
        for their clients. Support team member cannot create contracts.

        Foreign key relationships are done through pk, in our case the id. However, that
        pk shouldn't be public. Thus, we use the first name and last name fields to query
        the client instance related to the created contract."""
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
    """The update method ensures an authenticated user can update a Contract instance according to his
    permissions. The destroy method ensures an authenticated user can delete a Contract instance
    according to his permissions.

    Foreign key relationships are done through pk, in our case the id. However, that
    pk shouldn't be public. Thus, we use the first name and last name fields to query
    the client instance related to the updated contract Similarly, the username is used
    to query the CustomUser related to the updated contract.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContractSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        contract_title = kwargs["contract_title"]
        contract = Contract.objects.get(title=contract_title)

        if request.user.user_type in [1, 2]:
            """Managers have edit access to all contracts. Salesmen can only modify their clients'
             contracts. And salesmen cannot change the sales_contact field. Support team members 
             cannot modify contracts."""
            salesman_clients = Client.objects.filter(sales_contact=request.user.id)
            if request.user.user_type == 2 and contract.client not in salesman_clients:
                raise PermissionDenied("Salesmen can edit only their clients' contracts.")

            if request.user.user_type == 2 and request.data["sales_contact"] != contract.sales_contact:
                raise PermissionDenied("Salesmen cannot change the sales_contact field")

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
            raise PermissionDenied("Only managers and support team members can edit contracts")

    def destroy(self, request, *args, **kwargs):
        """Managers can delete any contract. Salesmen can only delete their clients' contracts.
        Support team member cannot delete contracts.
        """
        contract_title = kwargs["contract_title"]
        contract = Contract.objects.get(title=contract_title)
        if request.user.user_type in [1, 2]:
            salesman_clients = Client.objects.filter(sales_contact=request.user.id)
            if request.user.user_type == 2 and contract.client not in salesman_clients:
                raise PermissionDenied("Salesmen can delete only their clients' contracts.")
            contract.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type == 3:
            raise PermissionDenied("Only managers and salesmen can delete contracts.")


class EventView(APIView):
    """The get method ensures an authenticated user can access the Event model according to his
    permissions.

    Foreign key relationships are done through pk, in our case the id. However, that
    pk shouldn't be public. Thus, we use the username field to query the CustomUser related to the
    requested event. Similarly, we use the title to query the Contract related to the requested event."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Any authenticated user has read access to all events."""
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
    """The create method ensures an authenticated user can create an Event instance according to his
    permissions.

    Foreign key relationships are done through pk, in our case the id. However, that
    pk shouldn't be public. Thus, we use the username field to query the CustomUser related to the
    created event. Similarly, we use the title to query the Contract related to the created event."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        """Only managers and salesmen can create events.
        Salesmen can only create events for their clients."""
        if request.user.user_type in [1, 2]:
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
    """The update method ensures an authenticated user can update an Event instance according to his
    permissions. The destroy method ensures an authenticated user can delete an Event instance
    according to his permissions.

    Foreign key relationships are done through pk, in our case the id. However, that
    pk shouldn't be public. Thus, we use the username field to query the CustomUser related to the
    updated event. Similarly, we use the title to query the Contract related to the updated event."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventSerializer
    http_method_names = ["put", "delete"]

    def update(self, request, *args, **kwargs):
        """Managers can modify all events. Salesmen can only modify their clients' events.
        Similarly, support team member can only modify events they are assigned to until they happen."""
        event_title = kwargs["event_title"]
        event = Event.objects.get(title=event_title)

        if request.user.user_type in [1, 2]:
            if request.user.user_type == 2 and event.contract.sales_contact != request.user:
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
                raise PermissionDenied("Support team members can only edit their events")
            if event.event_date < timezone.now():
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

    def destroy(self, request, *args, **kwargs):
        """Managers can delete all events. Salesmen can only delete their clients' events.
        However, support team member cannot delete events."""
        event_title = kwargs["event_title"]
        event = Event.objects.get(title=event_title)
        if request.user.user_type == 1:
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.user.user_type == 2:
            if event.contract.sales_contact == request.user:
                event.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise PermissionDenied("Salesmen can only delete their clients' events.")
        elif request.user.user_type == 3:
            raise PermissionDenied("Support team member can only delete their clients' events.")
