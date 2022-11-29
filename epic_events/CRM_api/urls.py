from django.urls import path, include
from .views import ClientApiView

urlpatterns = [
    path('api', ClientApiView.as_view()),
]