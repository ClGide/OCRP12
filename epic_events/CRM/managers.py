from django.contrib.auth.models import BaseUserManager
import numpy
# just to check git works on this project


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, email, first_name, last_name, user_type, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("all users must have is_staff=True.")
        if not username:
            raise ValueError("username for user must be set.")
        if not email:
            raise ValueError("email for user must be set.")
        if not first_name:
            raise ValueError("first name for user must be set.")
        if not last_name:
            raise ValueError("last name for user must be set.")
        if not user_type:
            raise ValueError("user type for user must be set.")
        # phone is an optional arg, I guess it will be passed through **extra_fields
        user = self.model(username=username, first_name=first_name,
                          last_name=last_name, user_type=user_type,
                          email=self.normalize_email(email),
                          **extra_fields)   # if not passed as kwargs, will complain that we gave id a str (username)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, email, first_name, last_name, user_type, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_super") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        # if not passed as kwargs, will complain that we gave id a str (username)
        return self.create_user(username=username, password=password,
                                email=self.normalize_email(email),
                                first_name=first_name,
                                last_name=last_name, user_type=user_type,
                                **extra_fields)
