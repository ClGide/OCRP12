from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from django.forms import ModelForm


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        exclude = "__all__"


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = "__all__"


class ClientForm(ModelForm):

    class Meta:
        model = Client
        fields = "__all__"

