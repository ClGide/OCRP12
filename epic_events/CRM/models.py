from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator


class Client(models.Model):
    first_name = models.CharField(max_length=25, db_index=True)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    company_name = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    client_status = models.ForeignKey("ClientStatus", on_delete=models.SET_NULL, null=True)
    sales_contact = models.ForeignKey("CustomUser", on_delete=models.CASCADE)

    def __str__(self):
        return f"client {self.first_name} {self.last_name}"


class ClientStatus(models.Model):
    status = models.CharField(max_length=25)
    description = models.TextField()

    def __str__(self):
        return f"client status: {self.status}"


class Contract(models.Model):
    signed = models.BooleanField(help_text="If set to True, the contract is signed")
    amount = models.FloatField()
    payment_due = models.FloatField()
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    sales_contact = models.ForeignKey("CustomUser", on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey("Client", on_delete=models.CASCADE)

    def __str__(self):
        if self.signed:
            return f"{self.client} contract's signed with {self.sales_contact} for {self.amount}"
        else:
            return f"{self.client} contract's to be signed with {self.sales_contact} for {self.amount}"


class Event(models.Model):
    status = models.BooleanField()
    attendees = models.IntegerField()
    event_date = models.DateTimeField()
    notes = models.TextField()
    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    support_contact = models.ForeignKey("CustomUser", on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    contract = models.ForeignKey("Contract", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.client} event's. Date: {self.event_date}"


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, "manage team"),
        (2, "sales team"),
        (3, "support team")
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)


@receiver(post_save, sender=CustomUser)
def set_staff_superuser_for_new_users(sender, **kwargs):
    new_user = kwargs.get("instance")
    new_user.is_staff = True
    if new_user.user_type == 1:
        new_user.is_superuser = True
