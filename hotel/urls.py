from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
    path('room/<int:room_id>/book/', views.book_room, name='book_room'),
    path('bookings/', views.user_bookings, name='user_bookings'),
    path('register/', views.register, name='register'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),  # Add this line
]