from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from backend.api.models import (
    Badge,
    BggGame,
    Event,
    LibraryGame,
    Location,
    Order,
    Quota,
    Ticket,
    Withdraw,
)

User = get_user_model()

admin.site.register(User, UserAdmin)


@admin.register(BggGame)
class BggGameAdmin(admin.ModelAdmin):
    fields = ("name", "bggid", "badges")
    list_display = ("name", "bggid", "rank")
    readonly_fields = (
        "bggid",
        "name",
    )
    ordering = ("name",)


admin.site.register(Badge)


@admin.register(LibraryGame)
class LibraryGameAdmin(admin.ModelAdmin):
    search_fields = ["game__name", "notes"]
    list_display = (
        "game",
        "owner",
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    ordering = ("name", "type")


@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ("game", "requisitor", "duration")
    ordering = ("game", "requisitor")


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):
    list_display = ("user", "year")
    ordering = ("-year", "user")
    search_fields = ["user__first_name", "user__last_name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total", "is_payed")
    readonly_fields = ("user", "products", "total")
    ordering = ("user",)
    search_fields = ["user__first_name", "user__last_name", "user__email"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    ordering = ("type",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    ordering = ("name",)
