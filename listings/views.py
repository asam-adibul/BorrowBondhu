from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Listing
from .forms import ListingForm


def is_admin(user):
    return user.is_superuser


def listing_list(request):
    from django.core.paginator import Paginator
    listings = Listing.objects.filter(approved=True, is_available=True)

    query     = request.GET.get('q', '')
    category  = request.GET.get('category', '')
    location  = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if query:
        listings = listings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category:
        listings = listings.filter(category=category)
    if location:
        listings = listings.filter(location__icontains=location)
    if min_price:
        listings = listings.filter(price_per_day__gte=min_price)
    if max_price:
        listings = listings.filter(price_per_day__lte=max_price)

    paginator = Paginator(listings, 12)
    page      = request.GET.get('page')
    listings  = paginator.get_page(page)

    categories = Listing.CATEGORY_CHOICES
    return render(request, 'listings/listing_list.html', {
        'listings':          listings,
        'categories':        categories,
        'query':             query,
        'selected_category': category,
        'location':          location,
        'min_price':         min_price,
        'max_price':         max_price,
    })


def listing_detail(request, pk):
    listing    = get_object_or_404(Listing, pk=pk, approved=True)
    reviews    = listing.reviews.select_related('reviewer').order_by('-created_at')
    avg_rating = listing.average_rating()
    active_booking = listing.active_booking()
    return render(request, 'listings/listing_detail.html', {
        'listing':        listing,
        'reviews':        reviews,
        'avg_rating':     avg_rating,
        'active_booking': active_booking,
    })


@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing         = form.save(commit=False)
            listing.owner   = request.user
            listing.approved = False
            listing.save()
            messages.success(request, 'Listing submitted! It will appear after admin approval.')
            return redirect('my_listings')
    else:
        form = ListingForm()
    return render(request, 'listings/listing_form.html', {'form': form, 'action': 'Create'})


@login_required
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            listing          = form.save(commit=False)
            listing.approved = False
            listing.save()
            messages.success(request, 'Listing updated! Pending re-approval.')
            return redirect('my_listings')
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/listing_form.html', {'form': form, 'action': 'Edit'})


@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted.')
        return redirect('my_listings')
    return render(request, 'listings/listing_confirm_delete.html', {'listing': listing})


@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'listings/my_listings.html', {'listings': listings})


@login_required
@user_passes_test(is_admin)
def pending_approvals(request):
    """Admin page showing all listings pending approval."""
    pending  = Listing.objects.filter(approved=False).select_related('owner').order_by('-created_at')
    approved = Listing.objects.filter(approved=True).select_related('owner').order_by('-created_at')[:10]
    return render(request, 'listings/pending_approvals.html', {
        'pending':  pending,
        'approved': approved,
    })


@login_required
@user_passes_test(is_admin)
def approve_listing(request, pk):
    """Approve a single listing."""
    listing          = get_object_or_404(Listing, pk=pk)
    listing.approved = True
    listing.save()
    messages.success(request, f'"{listing.title}" has been approved and is now live.')
    return redirect('pending_approvals')


@login_required
@user_passes_test(is_admin)
def reject_listing(request, pk):
    """Reject/unapprove a listing."""
    listing          = get_object_or_404(Listing, pk=pk)
    listing.approved = False
    listing.save()
    messages.warning(request, f'"{listing.title}" has been unapproved.')
    return redirect('pending_approvals')


@login_required
def listing_preview(request, pk):
    """Preview an unapproved listing — accessible by owner and admin."""
    listing = get_object_or_404(Listing, pk=pk)
    if not request.user.is_superuser and listing.owner != request.user:
        messages.error(request, 'You do not have access to preview this listing.')
        return redirect('listing_list')
    reviews        = listing.reviews.select_related('reviewer').order_by('-created_at')
    avg_rating     = listing.average_rating()
    active_booking = listing.active_booking()
    return render(request, 'listings/listing_detail.html', {
        'listing':        listing,
        'reviews':        reviews,
        'avg_rating':     avg_rating,
        'active_booking': active_booking,
        'is_preview':     True,
    })


@login_required
@user_passes_test(is_admin)
def damage_reports(request):
    from bookings.models import Booking
    reports = Booking.objects.filter(
        is_damaged=True
    ).select_related(
        'listing', 'listing__owner', 'renter'
    ).order_by('-damage_reported_at')

    return render(request, 'listings/damage_reports.html', {
        'reports': reports,
    })


