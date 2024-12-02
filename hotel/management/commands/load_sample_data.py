from django.core.management.base import BaseCommand
from hotel.models import RoomCategory, Room  # Changed from hotel_project.hotel.models
import os
import urllib.request
from django.conf import settings

class Command(BaseCommand):
    help = 'Loads sample data into the database'

    def handle(self, *args, **kwargs):
        # Create media directory if it doesn't exist
        media_root = settings.MEDIA_ROOT
        rooms_dir = os.path.join(media_root, 'rooms')
        os.makedirs(rooms_dir, exist_ok=True)

        # Create categories
        self.stdout.write('Creating room categories...')

        # Create Люкс category
        lux, _ = RoomCategory.objects.get_or_create(
            name='Люкс',
            defaults={
                'description': 'Просторный номер с гостиной зоной, спальней и джакузи',
                'price': 200.00
            }
        )

        # Create Полулюкс category
        semi_lux, _ = RoomCategory.objects.get_or_create(
            name='Полулюкс',
            defaults={
                'description': 'Комфортный номер с раздельными зонами для отдыха и сна',
                'price': 150.00
            }
        )

        # Create Стандарт category
        standard, _ = RoomCategory.objects.get_or_create(
            name='Стандарт',
            defaults={
                'description': 'Уютный номер со всем необходимым для комфортного проживания',
                'price': 100.00
            }
        )

        # Create rooms
        rooms_data = [
            {'number': '101', 'category': lux, 'capacity': 3},
            {'number': '102', 'category': lux, 'capacity': 3},
            {'number': '201', 'category': semi_lux, 'capacity': 2},
            {'number': '202', 'category': semi_lux, 'capacity': 2},
            {'number': '203', 'category': semi_lux, 'capacity': 2},
            {'number': '301', 'category': standard, 'capacity': 2},
            {'number': '302', 'category': standard, 'capacity': 2},
            {'number': '303', 'category': standard, 'capacity': 2},
            {'number': '304', 'category': standard, 'capacity': 2},
            {'number': '305', 'category': standard, 'capacity': 2},
        ]

        for data in rooms_data:
            room, created = Room.objects.get_or_create(
                room_number=data['number'],
                defaults={
                    'category': data['category'],
                    'capacity': data['capacity']
                }
            )
            if created:
                self.stdout.write(f'Created room {data["number"]}')
            else:
                self.stdout.write(f'Room {data["number"]} already exists')

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data'))