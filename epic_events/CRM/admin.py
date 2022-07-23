from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import *
from .models import *


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ["email", "username", "user_type"]
    fieldsets = (
        (None, {"fields": ("username",
                           'user_type',)}),
        ("Personal info", {"fields": ("first_name",
                                      "last_name",
                                      "email",
                                      "phone")}),
    )

    add_fieldsets = (
        (None, {"fields": ("username",
                           "password1",
                           "password2",
                           'user_type',)}),
        ("Personal info", {"fields": ("first_name",
                                      "last_name",
                                      "email",
                                      "phone")}),

    )


class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    readonly_fields = ["client_status"]


class EventAdmin(admin.ModelAdmin):
    form = EventForm
    readonly_fields = ["status"]


class ContractAdmin(admin.ModelAdmin):
    form = ContractForm


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Event, EventAdmin)
#admin.site.unregister(Group)




