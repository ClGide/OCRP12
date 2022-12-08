"""We use a custom User model. Thus, we have to specify a custom Manager"""

from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """Specifies required fields and values to create an instance of the User model.

    A superuser is an instance of the User model just as any other user created with the
    create_user method. The is_superuser is the main difference. It gives elevated permissions
    to superusers.
    """
    def create_user(self, username, password, email,
                    first_name, last_name, user_type, **extra_fields):
        """Raises a Value Error if any of the is_staff, username, email,
        first_name, last_name or user_type isn't set. Then uses the received
        data to create an User instance."""
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

    def create_superuser(self, username, password, email,
                         first_name, last_name, user_type, **extra_fields):
        """Raises a ValueError if the is_superuser isn't set. Also raises a ValueError if any
        of the field checked by self.create_user isn't set. Then creates a User instance with
        the received data."""
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_super") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        # if not passed as kwargs, will complain that we gave id a str (username)
        return self.create_user(username=username, password=password,
                                email=self.normalize_email(email),
                                first_name=first_name,
                                last_name=last_name, user_type=user_type,
                                **extra_fields)
