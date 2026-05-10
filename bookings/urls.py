from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:listing_pk>/', views.booking_create, name='booking_create'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('<int:pk>/<str:action>/', views.booking_action, name='booking_action'),
]