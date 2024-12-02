from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Avg, Count
from django.core.exceptions import ValidationError
from .models import Room, Booking, RoomCategory, Client
from .forms import BookingForm, UserRegistrationForm


def home(request):
    """Home page view showing room categories"""
    categories = RoomCategory.objects.annotate(
        room_count=Count('room'),
        avg_price=Avg('room__booking__total_price')
    )
    return render(request, 'hotel/home.html', {'categories': categories})


def room_list(request):
    """View for displaying and filtering rooms"""
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    rooms = Room.objects.all()
    categories = RoomCategory.objects.all()

    if category_id:
        rooms = rooms.filter(category_id=category_id)
    if min_price:
        rooms = rooms.filter(category__price__gte=min_price)
    if max_price:
        rooms = rooms.filter(category__price__lte=max_price)

    context = {
        'rooms': rooms,
        'categories': categories
    }
    return render(request, 'hotel/room_list.html', context)


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Create client profile
                Client.objects.create(
                    user=user,
                    phone_number=form.cleaned_data['phone_number'],
                    date_of_birth=form.cleaned_data['date_of_birth']
                )
                login(request, user)
                messages.success(request, 'Регистрация успешна!')
                return redirect('home')
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def book_room(request, room_id):
    """View for booking a room"""
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.room = room
                booking.client = request.user.client
                booking.save()
                messages.success(request, 'Бронирование успешно создано!')
                return redirect('user_bookings')
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = BookingForm()
    return render(request, 'hotel/booking_form.html', {'form': form, 'room': room})


@login_required
def user_bookings(request):
    """View for displaying user's bookings"""
    try:
        bookings = Booking.objects.filter(client=request.user.client)
        return render(request, 'hotel/user_bookings.html', {'bookings': bookings})
    except Client.DoesNotExist:
        messages.error(request, 'Пожалуйста, заполните информацию о себе')
        return redirect('create_client_profile')


@login_required
def create_client_profile(request):
    """View for creating client profile"""
    if hasattr(request.user, 'client'):
        messages.info(request, 'У вас уже есть профиль клиента')
        return redirect('user_bookings')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')

        if phone_number and date_of_birth:
            try:
                Client.objects.create(
                    user=request.user,
                    phone_number=phone_number,
                    date_of_birth=date_of_birth
                )
                messages.success(request, 'Профиль успешно создан!')
                return redirect('user_bookings')
            except ValidationError as e:
                messages.error(request, str(e))

    return render(request, 'hotel/create_client_profile.html')


@login_required
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, client=request.user.client)
        if booking.status == 'pending':
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Бронирование успешно отменено')
        else:
            messages.error(request, 'Это бронирование нельзя отменить')
    return redirect('user_bookings')