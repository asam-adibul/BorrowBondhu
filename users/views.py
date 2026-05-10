from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, ProfileForm
from .models import Profile
from listings.models import Listing
from bookings.models import Booking


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user            = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            user.email      = form.cleaned_data['email']
            user.save()

            # Save phone to profile
            profile       = Profile.objects.create(user=user)
            profile.phone = form.cleaned_data['phone']
            profile.save()

            login(request, user)
            messages.success(request, f'Welcome to BorrowBondhu, {user.first_name}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name  = request.POST.get('last_name',  request.user.last_name)
            request.user.email      = request.POST.get('email',      request.user.email)
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/profile.html', {'form': form})


@login_required
def dashboard_view(request):
    from django.utils import timezone
    from django.db.models import Q
    today = timezone.now().date()

    # My listings
    my_listings    = Listing.objects.filter(owner=request.user).order_by('-created_at')
    approved_count = my_listings.filter(approved=True).count()
    pending_count  = my_listings.filter(approved=False).count()

    # Bookings I made (renting)
    my_rents      = Booking.objects.filter(renter=request.user).select_related('listing').order_by('-created_at')
    active_rents  = my_rents.filter(status='accepted', end_date__gte=today)
    pending_rents = my_rents.filter(status='pending')

    # Auto-mark expired accepted bookings as completed
    my_rents.filter(status='accepted', end_date__lt=today).update(status='completed')

    # Re-fetch after update
    my_rents      = Booking.objects.filter(renter=request.user).select_related('listing').order_by('-created_at')
    active_rents  = my_rents.filter(status__in=['accepted', 'received'], end_date__gte=today)
    pending_rents = my_rents.filter(status='pending')

    # Requests on my listings (as owner)
    my_requests      = Booking.objects.filter(listing__owner=request.user).select_related('listing', 'renter').order_by('-created_at')
    pending_requests = my_requests.filter(status='pending')
    active_requests  = my_requests.filter(status__in=['accepted', 'handed_over', 'received'])

    # Auto-mark expired owner bookings
    my_requests.filter(status__in=['accepted', 'received'], end_date__lt=today).update(status='completed')

    # Re-fetch
    my_requests      = Booking.objects.filter(listing__owner=request.user).select_related('listing', 'renter').order_by('-created_at')
    pending_requests = my_requests.filter(status='pending')
    active_requests  = my_requests.filter(status__in=['accepted', 'handed_over', 'received'])

    # Currently rented out
    currently_rented = my_requests.filter(
        status__in=['handed_over', 'received'],
        start_date__lte=today,
        end_date__gte=today
    )

    # Needs review
    from reviews.models import Review
    completed_rents = my_rents.filter(status='completed')
    reviewed_ids    = Review.objects.filter(reviewer=request.user).values_list('booking_id', flat=True)
    needs_review    = completed_rents.exclude(id__in=reviewed_ids).count()

    recent_rents    = my_rents[:5]
    recent_requests = my_requests[:5]
    recent_listings = my_listings[:4]

    return render(request, 'users/dashboard.html', {
        'my_listings':        my_listings,
        'approved_count':     approved_count,
        'pending_count':      pending_count,
        'my_rents':           my_rents,
        'active_rents':       active_rents,
        'pending_rents':      pending_rents,
        'my_requests':        my_requests,
        'pending_requests':   pending_requests,
        'active_requests':    active_requests,
        'currently_rented':   currently_rented,
        'needs_review':       needs_review,
        'recent_rents':       recent_rents,
        'recent_requests':    recent_requests,
        'recent_listings':    recent_listings,
        'today':              today,
    })