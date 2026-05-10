from django.contrib import admin
from django.utils.html import format_html
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'renter', 'listing', 'start_date', 'end_date',
        'status', 'damage_indicator', 'created_at'
    ]
    list_filter   = ['status', 'is_damaged']
    search_fields = ['renter__username', 'listing__title', 'damage_description']
    readonly_fields = [
        'renter', 'listing', 'start_date', 'end_date',
        'status', 'message', 'created_at',
        'owner_confirmed_handover', 'renter_confirmed_receipt',
        'owner_marked_returned', 'renter_confirmed_return',
        'return_note', 'is_damaged', 'damage_description', 'damage_reported_at'
    ]

    fieldsets = (
        ('Booking Info', {
            'fields': ('renter', 'listing', 'start_date', 'end_date', 'status', 'message', 'created_at')
        }),
        ('Handover Tracking', {
            'fields': ('owner_confirmed_handover', 'renter_confirmed_receipt')
        }),
        ('Return Tracking', {
            'fields': ('owner_marked_returned', 'renter_confirmed_return', 'return_note')
        }),
        ('Damage Report', {
            'fields': ('is_damaged', 'damage_description', 'damage_reported_at'),
            'classes': ('collapse',) if False else (),
        }),
    )

    def damage_indicator(self, obj):
        if obj.is_damaged:
            return format_html(
                '<span style="background:#fef2f2;color:#991b1b;padding:3px 10px;'
                'border-radius:50px;font-weight:700;font-size:11px;">'
                '⚠ DAMAGED</span>'
            )
        return format_html(
            '<span style="color:#16a34a;font-size:11px;">✓ OK</span>'
        )
    damage_indicator.short_description = 'Damage'


class DamagedBookingProxy(Booking):
    class Meta:
        proxy = True
        verbose_name = 'Damage Report'
        verbose_name_plural = '⚠ Damage Reports'


@admin.register(DamagedBookingProxy)
class DamageReportAdmin(admin.ModelAdmin):
    list_display = [
        'listing_title', 'owner_name', 'renter_name',
        'rental_dates', 'damage_reported_at', 'damage_preview'
    ]
    search_fields = ['listing__title', 'renter__username', 'listing__owner__username', 'damage_description']
    readonly_fields = [
        'renter', 'listing', 'start_date', 'end_date',
        'damage_description', 'damage_reported_at',
        'return_note', 'owner_marked_returned', 'renter_confirmed_return'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_damaged=True)

    def listing_title(self, obj):
        return format_html('<strong>{}</strong>', obj.listing.title)
    listing_title.short_description = 'Item'

    def owner_name(self, obj):
        return obj.listing.owner.get_full_name() or obj.listing.owner.username
    owner_name.short_description = 'Owner'

    def renter_name(self, obj):
        return obj.renter.get_full_name() or obj.renter.username
    renter_name.short_description = 'Renter'

    def rental_dates(self, obj):
        return f"{obj.start_date.strftime('%b %d')} → {obj.end_date.strftime('%b %d, %Y')}"
    rental_dates.short_description = 'Rental Period'

    def damage_preview(self, obj):
        preview = obj.damage_description[:80] + '...' if len(obj.damage_description) > 80 else obj.damage_description
        return format_html(
            '<span style="color:#991b1b;">{}</span>', preview
        )
    damage_preview.short_description = 'Damage Description'

    fieldsets = (
        ('Item & Rental Info', {
            'fields': ('listing', 'renter', 'start_date', 'end_date')
        }),
        ('Damage Report Details', {
            'fields': ('damage_description', 'damage_reported_at')
        }),
        ('Return Details', {
            'fields': ('return_note', 'owner_marked_returned', 'renter_confirmed_return')
        }),
    )