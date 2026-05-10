from django.db import models
from django.contrib.auth.models import User
from listings.models import Listing


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, help_text="Optional message to the owner")

    def __str__(self):
        return f"{self.renter.username} → {self.listing.title} ({self.status})"

    def total_days(self):
        return (self.end_date - self.start_date).days or 1

    def total_price(self):
        return self.total_days() * self.listing.price_per_day