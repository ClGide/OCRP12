"""Defines four models used in both the crm and api app."""


from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .managers import CustomUserManager


class Client(models.Model):
    """There's a unique together constraint on the first_name and last_name
    fields. It's thus encouraged to make your queries based on those two
    fields.
    You cannot use whitespaces in the first_name or last_name."""
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    company_name = models.CharField(max_length=250)
    CLIENT_STATUS_CHOICES = (
        (1, "potential"),
        (2, "existent with at least one upcoming event."),
        (3, "existent with at least one past event.")
    )

    client_status = models.PositiveSmallIntegerField(choices=CLIENT_STATUS_CHOICES, default=1)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    sales_contact = models.ForeignKey("CustomUser",
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      limit_choices_to=Q(user_type=2))  # type 2 is sales team

    class Meta:
        unique_together = [['first_name', 'last_name']]

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email}"

    def clean(self):
        """first name and last name shouldn't contain spaces."""
        if " " in self.first_name:
            raise ValidationError("there should be no spaces in the first name")
        if " " in self.last_name:
            raise ValidationError("there should be no spaces in the last name")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Contract(models.Model):
    """The title field is unique. It's thus encouraged to make queries based on it. Because
     this field is used in the URL, it can't contain special characters."""
    title = models.CharField(max_length=50, unique=True, help_text="do not use special characters")
    signed = models.BooleanField(help_text="tick if the contract is signed")
    amount = models.FloatField()
    payment_due = models.FloatField()
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    sales_contact = models.ForeignKey("CustomUser",
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      limit_choices_to=Q(user_type=2))  # type 2 is sales team
    client = models.ForeignKey("Client", on_delete=models.CASCADE)

    def clean(self):
        """checks that all char can fit in a URL. If there are special char,
        raises a ValidationError as the user knows he shouldn't use such char in the title.
        If there are spaces, replaces them by '_'."""
        validated_title = ""
        for ch in str(self.title):
            if not ch.isalnum() and ch != " ":
                raise ValidationError("Do not use special chars in the title")
            if ch == " ":
                validated_title += "_"
            else:
                validated_title += ch
        self.title = validated_title
        if self.payment_due > self.amount:
            raise ValidationError("The payment due cannot be superior to the "
                                  "total amount.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Event(models.Model):
    """The title field is unique. It's thus encouraged to make queries based on it. Because
     this field is used in the URL, it can't contain special characters."""
    title = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(
        help_text="green if the event already took place",
        blank=True,
        default=False,
    )
    attendees = models.IntegerField()
    event_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    support_contact = models.ForeignKey("CustomUser",
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        limit_choices_to=Q(user_type=3))  # type 3 is support team
    contract = models.ForeignKey("Contract", on_delete=models.CASCADE)

    def clean(self):
        """checks that all char can fit in a URL. If there are special char,
        raises a ValidationError as the user knows he shouldn't use such char in the title.
        If there are spaces, replaces them by '_'."""
        validated_title = ""
        for ch in str(self.title):
            if not ch.isalnum() and ch != " ":
                raise ValidationError("Do not use special chars in the title")
            if ch == " ":
                validated_title += "_"
            else:
                validated_title += ch
        self.title = validated_title

    def save(self, *args, **kwargs):
        """The field status is automatically updated everytime the object is saved."""
        if self.event_date < timezone.now():
            self.status = True
        else:
            self.status = False
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CustomUser(AbstractUser):
    """username field is required and inherited. There's also a unique constraint
    on that field. It's thus encouraged to make queries based on that field."""
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField()

    USER_TYPE_CHOICES = (
        (1, "management team"),
        (2, "sales team"),
        (3, "support team")
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email", "user_type"]

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    objects = CustomUserManager()

    class Meta:
        constraints = [models.UniqueConstraint('username', name="username_unique")]

    def clean(self):
        """Ensures all users have the is_staff permission needed to access the admin interface. Also
        ensures all managers have superuser elevated permissions"""
        self.is_staff = True
        if self.user_type == 1:
            self.is_superuser = True

    def has_perm(self, perm, obj=None):
        """Must return True if the User has the specified permission 'perm'. We always return
        True because permissions are checked in api/views.py and crm/admin.py."""
        return True

    def has_module_perms(self, app_label):
        """Must return True if the User has any permission in the package 'app_label'."""
        return True

    def __str__(self):
        return self.username


@receiver(post_save, sender=Event)
def update_client_status(sender, **kwargs):
    """Registers on the client instance the fact that he has or not at
    least one upcoming/past event."""
    event = kwargs.get("instance")
    contract = event.contract
    client = contract.client
    # if the client already has a past event, his status
    # won't change.
    if client.client_status != 3:
        if client.client_status == 2:
            if event.status is True:
                client.client_status = 3
                client.save()
        elif client.client_status == 1:
            if event.status is False:
                client.client_status = 2
                client.save()
