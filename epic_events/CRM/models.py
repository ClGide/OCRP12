from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from .managers import CustomUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q


class Client(models.Model):
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
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    sales_contact = models.ForeignKey("CustomUser",
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      limit_choices_to=Q(user_type=2))  # type 2 is sales team

    class Meta:
        unique_together = [['first_name', 'last_name']]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Contract(models.Model):
    title = models.CharField(max_length=50, unique=True)
    signed = models.BooleanField(help_text="tick if the contract is signed")
    amount = models.FloatField()
    payment_due = models.FloatField()
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    sales_contact = models.ForeignKey("CustomUser",
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      limit_choices_to=Q(user_type=2))  # type 2 is sales team
    client = models.ForeignKey("Client", on_delete=models.CASCADE)

    def clean(self):
        if self.payment_due > self.amount:
            raise ValidationError("The payment due cannot be superior to the "
                                  "total amount.")

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(
        help_text="green if the event already took place",
        blank=True,
        default=False,
    )
    attendees = models.IntegerField()
    event_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    support_contact = models.ForeignKey("CustomUser",
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        limit_choices_to=Q(user_type=3))    # type 3 is support team
    contract = models.ForeignKey("Contract", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.event_date < timezone.now():
            self.status = True
        else:
            self.status = False
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class CustomUser(AbstractUser):
    # username field is required and inherited.
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField()

    USER_TYPE_CHOICES = (
        (1, "manage team"),
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

    def clean(self):
        self.is_staff = True
        if self.user_type == 1:
            self.is_superuser = True

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


@receiver(post_save, sender=Event)
def update_client_status(sender, **kwargs):
    event = kwargs.get("instance")
    contract = event.contract
    client = contract.client
    # if the client already has an past event, his status
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
