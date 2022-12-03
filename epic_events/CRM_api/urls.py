from django.urls import path, include
from .views import ClientView, ClientViewSet, CreateClientView
from .views import EventView, EventViewSet, CreateEventView
from .views import ContractView, ContractViewSet, CreateContractView


app_name = "CRM"

urlpatterns = [
    path('client/view', ClientView.as_view()),

    path('client/create', CreateClientView.as_view()),

    path('client/<slug:last_name>/<slug:first_name>/', ClientViewSet.as_view({
        "put": "update",
        "delete": "destroy"
    })),

    path('contract/view', ContractView.as_view()),

    path('contract/create', CreateContractView.as_view()),

    path('contract/<slug:contract_title>', ContractViewSet.as_view({
        "put": "update",
        "delete": "destroy"
    })),

    path('event/view', EventView.as_view()),

    path('event/create', CreateEventView.as_view()),

    path('event/<slug:event_title>', EventViewSet.as_view({
        "put": "update",
        "delete": "destroy"
    })),
]

