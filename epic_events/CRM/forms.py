from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField

from .models import *
from django.forms import ModelForm, CharField, PasswordInput


class CustomUserCreationForm(UserCreationForm):

    password1 = CharField(label='Password', widget=PasswordInput)
    password2 = CharField(label='Password confirmation', widget=PasswordInput)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["username", "password",
                  "user_type", "first_name",
                  "last_name", "email", "phone"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField()

    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = ["username", "password",
                  "user_type", "first_name",
                  "last_name", "email", "phone"]


