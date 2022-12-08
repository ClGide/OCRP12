"""We use a custom User model. Thus, we have to specify its custom forms.

Those forms are used in the admin site. The get_user_model() used throughout
this module retrieves the model specified in the settings. This model is
defined in models.py"""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.forms import CharField, PasswordInput


class CustomUserCreationForm(UserCreationForm):
    """Ensures all fields needed to create a User instance are requested"""
    password1 = CharField(label='Password', widget=PasswordInput)
    password2 = CharField(label='Password confirmation', widget=PasswordInput)

    class Meta(UserCreationForm.Meta):
        # Without the below lines, Django wouldn't use your custom
        # user fields in the form.
        model = get_user_model()
        fields = ["username", "password",
                  "user_type", "first_name",
                  "last_name", "email", "phone"]

    def clean_password2(self):
        """Ensures self.password1 and self.password2 are non-null and
        identical."""
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
    """Ensures all fields needed to modify a User instance are requested."""
    password = ReadOnlyPasswordHashField()

    class Meta(UserChangeForm.Meta):
        # Without the below lines, Django wouldn't use your custom
        # user fields in the form.
        model = get_user_model()
        fields = ["username", "password",
                  "user_type", "first_name",
                  "last_name", "email", "phone"]
