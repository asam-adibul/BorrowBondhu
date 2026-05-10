from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'category', 'price_per_day', 'location', 'approved', 'is_available', 'created_at']
    list_filter = ['approved', 'category', 'is_available']
    search_fields = ['title', 'owner__username', 'location']
    list_editable = ['approved', 'is_available']
    actions = ['approve_listings']

    def approve_listings(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, f'{queryset.count()} listings approved.')
    approve_listings.short_description = 'Approve selected listings'