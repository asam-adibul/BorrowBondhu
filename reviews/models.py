from django.db import models
from django.contrib.auth.models import User
from listings.models import Listing
from bookings.models import Booking


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} → {self.listing.title} ({self.rating}★)"