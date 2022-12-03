from django.urls import path, include
from .views import ClientView, ClientViewSet, CreateClientView
from .views import EventView, EventViewSet, CreateEventView
from .views import ContractView, ContractViewSet, CreateContractView
from .views import CustomUserView, CreateCustomUserView, CustomUserViewSet

app_name = "CRM"

urlpatterns = [
    path('users/view', CustomUserView.as_view()),

    path('users/create', CreateCustomUserView.as_view()),

    # trailing slash is needed OR set APPEND_SLASH=False in settings
    path('users/<slug:username>/', CustomUserViewSet.as_view({
        "put": "update",
        "delete": "destroy"
    })),

    path('client/view', ClientView.as_view()),

    path('client/create', CreateClientView.as_view()),

    # trailing slash is needed OR set APPEND_SLASH=False in settings
    path('client/<slug:first_name>/<slug:last_name>/', ClientViewSet.as_view({
        "put": "update",
        "delete": "destroy"
    })),

    path('contract/view', ContractView.as_view()),

    path('contract/create', CreateContractView.as_view()),

    # trailing slash is needed OR set APPEND_SLASH=False in settings
    path('contract/<slug:contract_title>', ContractViewSet.as_view({
        "put": "update",
        "delete": "destroy"
    })),

    path('event/view', EventView.as_view()),

    path('event/create', CreateEventView.as_view()),

    # trailing slash is needed OR set APPEND_SLASH=False in settings
    path('event/<slug:event_title>', EventViewSet.as_view({
        "put": "update",
        "delete": "destroy"
    })),
]

