from django.db import models


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
    sales_contact = models.ForeignKey("SalesTeamMember", on_delete=models.CASCADE)

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
    sales_contact = models.ForeignKey("SalesTeamMember", on_delete=models.SET_NULL)
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
    support_contact = models.ForeignKey("SupportTeamMember", on_delete=models.SET_NULL)
    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    contract = models.ForeignKey("Contract", on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.client} event's. Date: {self.event_date}"


