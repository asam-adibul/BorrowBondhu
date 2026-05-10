from .models import Listing


def pending_listings(request):
    if request.user.is_authenticated and request.user.is_superuser:
        from bookings.models import Booking
        pending_count = Listing.objects.filter(approved=False).count()
        damage_count  = Booking.objects.filter(is_damaged=True).count()
        return {
            'pending_listings_count': pending_count,
            'damage_reports_count':   damage_count,
        }
    return {
        'pending_listings_count': 0,
        'damage_reports_count':   0,
    }