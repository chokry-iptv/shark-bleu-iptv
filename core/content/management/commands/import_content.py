# content/management/commands/import_content.py
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from content.models import Movie, Series, Episode, LiveStream, Genre

class Command(BaseCommand):
    help = 'استيراد المحتوى من ملف CSV'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='مسار ملف CSV')

    def handle(self, *args, **options):
        file_path = options['file_path']
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if row['type'] == 'movie':
                        Movie.objects.get_or_create(
                            title=row['title'],
                            defaults={
                                'description': row['description'],
                                'thumbnail': row['thumbnail'],
                                'video_url': row['video_url'],
                                'release_year': int(row['release_year']) if row['release_year'] else 2024,
                                'is_public': row['is_public'] == '1',
                                'duration_minutes': 120,
                            }
                        )
                    elif row['type'] == 'live':
                        LiveStream.objects.get_or_create(
                            title=row['title'],
                            defaults={
                                'description': row['description'],
                                'thumbnail': row['thumbnail'],
                                'stream_url': row['video_url'],
                                'is_public': row['is_public'] == '1',
                                'is_active': True,
                            }
                        )
                    elif row['type'] == 'series':
                        Series.objects.get_or_create(
                            title=row['title'],
                            defaults={
                                'description': row['description'],
                                'thumbnail': row['thumbnail'],
                                'release_year': int(row['release_year']) if row['release_year'] else 2024,
                                'is_public': row['is_public'] == '1',
                            }
                        )
                    elif row['type'] == 'episode':
                        # هذا مثال بسيط — ستحتاج لربطه بمسلسل موجود
                        pass
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"خطأ في الصف: {row} - {e}"))
        self.stdout.write(self.style.SUCCESS('تم الاستيراد بنجاح!'))