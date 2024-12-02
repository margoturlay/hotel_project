from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from datetime import date

class RoomCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Room Categories"

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='rooms/', null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} - {self.category.name}"

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=19,
        validators=[
            RegexValidator(
                regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
                message="Phone number must be in format: +375 (29) XXX-XX-XX"
            )
        ]
    )
    date_of_birth = models.DateField()

    def clean(self):
        # Check if client is 18+
        if self.date_of_birth:
            age = (date.today() - self.date_of_birth).days / 365.25
            if age < 18:
                raise ValidationError('Clients must be 18 years or older')

    def __str__(self):
        return f"{self.user.get_full_name()}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    has_child = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.total_price:
            # Calculate total price based on number of days and room price
            days = (self.check_out_date - self.check_in_date).days
            self.total_price = self.room.category.price * days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.id} - {self.client.user.get_full_name()}"