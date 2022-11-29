from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import ClientSerializer
from rest_framework.response import Response
from rest_framework import status


class ClientApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(ClientSerializer.data, status=status.HTTP_200_OK)
