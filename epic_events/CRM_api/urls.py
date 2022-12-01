from django.urls import path, include
from .views import ClientView, ClientViewSet, CreateClientView
from .views import EventView, ContractView


app_name = "CRM"

urlpatterns = [
    path('client/create', CreateClientView.as_view()),

    path('client/view', ClientView.as_view()),

    path('event/view', EventView.as_view()),

    path('contract/view', ContractView.as_view()),

    path('client/<slug:last_name>/<slug:first_name>/', ClientViewSet.as_view({
        "put": "update",
    }))
]

