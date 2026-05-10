from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from listings.models import Listing
from .models import Booking
from .forms import BookingForm


@login_required
def booking_create(request, listing_pk):
    listing = get_object_or_404(Listing, pk=listing_pk, approved=True)

    # Guard 1 — Owner cannot book own item
    if listing.owner == request.user:
        messages.error(request, 'You cannot book your own listing.')
        return redirect('listing_detail', pk=listing_pk)

    # Guard 2 — Prevent duplicate pending requests
    already_requested = Booking.objects.filter(
        listing=listing,
        renter=request.user,
        status='pending'
    ).exists()

    if already_requested:
        messages.warning(request, 'You already have a pending request for this item. Wait for the owner to respond.')
        return redirect('listing_detail', pk=listing_pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data['start_date']
            end   = form.cleaned_data['end_date']

            # Guard 3 — End date must be after start date
            if end <= start:
                messages.error(request, 'End date must be after start date.')
                return render(request, 'bookings/booking_form.html', {
                    'form': form, 'listing': listing
                })

            # Guard 4 — Check for overlapping accepted bookings
            conflict = Booking.objects.filter(
                listing=listing,
                status='accepted',
                start_date__lt=end,
                end_date__gt=start
            ).exists()

            if conflict:
                messages.error(request, 'These dates overlap with an existing booking. Please choose different dates.')
                return render(request, 'bookings/booking_form.html', {
                    'form': form, 'listing': listing
                })

            # Guard 5 — Start date cannot be in the past
            from django.utils import timezone
            if start < timezone.now().date():
                messages.error(request, 'Start date cannot be in the past.')
                return render(request, 'bookings/booking_form.html', {
                    'form': form, 'listing': listing
                })

            # All checks passed — create booking
            booking = form.save(commit=False)
            booking.renter  = request.user
            booking.listing = listing
            booking.status  = 'pending'
            booking.save()

            messages.success(request, f'Booking request sent to {listing.owner.get_full_name() or listing.owner.username}! Wait for their response.')
            return redirect('my_bookings')
    else:
        form = BookingForm()

    return render(request, 'bookings/booking_form.html', {
        'form': form, 'listing': listing
    })


@login_required
def my_bookings(request):
    my_rents    = Booking.objects.filter(renter=request.user).select_related('listing').order_by('-created_at')
    my_requests = Booking.objects.filter(listing__owner=request.user).select_related('listing', 'renter').order_by('-created_at')
    return render(request, 'bookings/my_bookings.html', {
        'my_rents':    my_rents,
        'my_requests': my_requests,
    })


@login_required
def booking_action(request, pk, action):
    booking = get_object_or_404(Booking, pk=pk, listing__owner=request.user)

    if action == 'accept' and booking.status == 'pending':
        # Reject all other pending bookings for overlapping dates
        Booking.objects.filter(
            listing=booking.listing,
            status='pending',
            start_date__lt=booking.end_date,
            end_date__gt=booking.start_date
        ).exclude(pk=booking.pk).update(status='rejected')

        booking.status = 'accepted'
        messages.success(request, f'Booking accepted! Other overlapping requests have been automatically declined.')

    elif action == 'reject' and booking.status == 'pending':
        booking.status = 'rejected'
        messages.info(request, 'Booking declined.')

    elif action == 'complete' and booking.status == 'accepted':
        booking.status = 'completed'
        messages.success(request, 'Booking marked as completed.')

    else:
        messages.error(request, 'Invalid action.')

    booking.save()
    return redirect('my_bookings')