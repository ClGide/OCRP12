from django.contrib import admin
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

    # for the has_wiew_permission, we can keep the default

    def has_add_permission(self, request, obj=None):
        """Only managers can add new users.
        """
        if request.user.user_type == 1:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        """Only managers can change users.
        """
        if request.user.user_type == 1:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """Only managers can delete other users.
        """
        if request.user.user_type == 1:
            return True
        return False


class ClientAdmin(admin.ModelAdmin):
    model = Client
    readonly_fields = ["client_status"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(ClientAdmin, self).get_form(request, obj, **kwargs)
        if request.user.user_type == 2:
            if obj is None:
                form.base_fields["sales_contact"].initial = request.user
            # if he's not the assigned sale contact, he doesn't have access to
            # the sales contact field, so Django would complain if we try to
            # modify it.
            if obj.sales_contact == request.user:
                form.base_fields["sales_contact"].disabled = True
        return form

    def has_add_permission(self, request, obj=None):
        """Only managers and member of the sales team
        can add new clients.
        """
        if request.user.user_type in (1, 2):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        """Only managers and the member of the assigned member
        of the sales team can change clients.
        """
        if request.user.user_type == 1:
            return True
        if obj is not None:
            owner = obj.sales_contact
            if owner == request.user:
                return True
        return False

    def has_delete_permission(self, request, obj=None):
        """Only managers can delete other clients.
        """
        if request.user.user_type == 1:
            return True
        return False


class EventAdmin(admin.ModelAdmin):
    model = Event
    readonly_fields = ["status"]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """If a sales team member tries to create an event, he should base
        those events on a contract he contributed to as a sales contact."""
        if request.user.user_type == 2:
            if db_field.name == "contract":
                kwargs["queryset"] = Contract.objects.filter(sales_contact=request.user)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventAdmin, self).get_form(request, obj, **kwargs)
        if request.user.user_type == 3:
            # if he's not the assigned support member, he doesn't have access to
            # the support contact field, so Django would complain if we try to
            # modify it.
            if obj.support_contact == request.user:
                form.base_fields["support_contact"].disabled = True
        return form

    def has_add_permission(self, request, obj=None):
        """Only managers and member of the sales team
        can add new events.
        """
        if request.user.user_type in [1, 2]:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        """Only managers and the assigned member of the
        support team can change events (until the event
        happens).
        """
        if request.user.user_type == 1:
            return True
        if obj is not None:
            owner = obj.support_contact
            in_charge_sales_member = obj.contract.sales_contact
            # if status is set to True, then the event happened
            # and the assigned support member cannot change the
            # event anymore.
            if owner == request.user and not obj.status:
                return True
            if in_charge_sales_member == request.user and not obj.status:
                return True
        return False

    def has_delete_permission(self, request, obj=None):
        """Only managers can delete other events.
        """
        if request.user.user_type == 1:
            return True
        return False


class ContractAdmin(admin.ModelAdmin):
    model = Contract

    def get_form(self, request, obj=None, **kwargs):
        form = super(ContractAdmin, self).get_form(request, obj, **kwargs)
        if request.user.user_type == 2:
            if obj is None:
                form.base_fields["sales_contact"].initial = request.user
            # if he's not the assigned sale member, he doesn't have access to
            # the sales contact field, so Django would complain if we try to
            # modify it.
            if obj.sales_contact == request.user:
                form.base_fields["sales_contact"].disabled = True
        return form

    def has_add_permission(self, request, obj=None):
        """Only managers and member of the sales team
        can add new contracts.
        """
        if request.user.user_type in [1, 2]:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        """Only managers and the member of the assigned member
        of the sales team can change contracts.
        """
        if request.user.user_type == 1:
            return True
        if obj is not None:
            owner = obj.sales_contact
            if owner == request.user:
                return True
        return False

    def has_delete_permission(self, request, obj=None):
        """Only managers can delete other admins.
        """
        if request.user.user_type == 1:
            return True
        return False


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Event, EventAdmin)
admin.site.unregister(Group)

