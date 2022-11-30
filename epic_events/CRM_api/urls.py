from django.urls import path, include
from .views import ClientView, EventView, ContractView, CreateClientView

app_name = "CRM"

urlpatterns = [
    path('client/create', CreateClientView.as_view()),

    path('client/view', ClientView.as_view()),

    path('event/view', EventView.as_view()),

    path('contract/view', ContractView.as_view()),
]

