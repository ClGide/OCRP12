from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import *
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username", "user_type"]


class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    readonly_fields = ["client_status"]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Contract)
admin.site.register(Event)




