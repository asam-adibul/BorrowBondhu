from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bookings.models import Booking
from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, renter=request.user, status='completed')

    # Check if review already exists
    if hasattr(booking, 'review'):
        messages.warning(request, 'You have already reviewed this booking.')
        return redirect('my_bookings')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.listing = booking.listing
            review.booking = booking
            review.save()
            messages.success(request, 'Review submitted! Thank you.')
            return redirect('listing_detail', pk=booking.listing.pk)
    else:
        form = ReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'booking': booking})