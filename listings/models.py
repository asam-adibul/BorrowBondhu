from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('cameras', 'Cameras & Photography'),
        ('electronics', 'Electronics'),
        ('tools', 'Tools & Equipment'),
        ('events', 'Event Equipment'),
        ('sports', 'Sports & Outdoors'),
        ('other', 'Other'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    def is_currently_booked(self):
        """Returns the active booking if item is booked today, else None."""
        today = timezone.now().date()
        return self.bookings.filter(
            status='accepted',
            start_date__lte=today,
            end_date__gte=today
        ).first()

    def active_booking(self):
        """Returns the current accepted booking if any."""
        return self.is_currently_booked()