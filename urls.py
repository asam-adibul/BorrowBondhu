from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from listings.views import listing_list  # home page


def home(request):
    from django.shortcuts import render
    from listings.models import Listing
    featured = Listing.objects.filter(approved=True, is_available=True).order_by('-created_at')[:6]
    return render(request, 'home.html', {'featured': featured})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('users/', include('users.urls')),
    path('listings/', include('listings.urls')),
    path('bookings/', include('bookings.urls')),
    path('reviews/', include('reviews.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)