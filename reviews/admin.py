from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'listing', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['reviewer__username', 'listing__title']