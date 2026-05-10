# from django.urls import path
# from . import views

# urlpatterns = [
#     path('',                        views.listing_list,       name='listing_list'),
#     path('create/',                 views.listing_create,     name='listing_create'),
#     path('my/',                     views.my_listings,        name='my_listings'),
#     path('approvals/',              views.pending_approvals,  name='pending_approvals'),
#     path('<int:pk>/',               views.listing_detail,     name='listing_detail'),
#     path('<int:pk>/edit/',          views.listing_edit,       name='listing_edit'),
#     path('<int:pk>/delete/',        views.listing_delete,     name='listing_delete'),
#     path('<int:pk>/approve/',       views.approve_listing,    name='approve_listing'),
#     path('<int:pk>/reject/',        views.reject_listing,     name='reject_listing'),
#     path('<int:pk>/preview/',       views.listing_preview,    name='listing_preview'),
# ]



from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.listing_list,                name='listing_list'),
    path('create/',                 views.listing_create,              name='listing_create'),
    path('my/',                     views.my_listings,                 name='my_listings'),
    path('approvals/',              views.pending_approvals,           name='pending_approvals'),
    path('damage-reports/',         views.damage_reports,              name='damage_reports'),
    path('<int:pk>/',               views.listing_detail,              name='listing_detail'),
    path('<int:pk>/edit/',          views.listing_edit,                name='listing_edit'),
    path('<int:pk>/delete/',        views.listing_delete,              name='listing_delete'),
    path('<int:pk>/approve/',       views.approve_listing,             name='approve_listing'),
    path('<int:pk>/reject/',        views.reject_listing,              name='reject_listing'),
    path('<int:pk>/preview/',       views.listing_preview,             name='listing_preview'),
    path('<int:pk>/toggle/',        views.listing_toggle_availability, name='listing_toggle'),
]