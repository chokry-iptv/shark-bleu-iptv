# content/management/commands/load_media.py
from django.core.management.base import BaseCommand
from django.conf import settings
from content.models import LiveStream
import json
import os

class Command(BaseCommand):
    help = 'تحميل القنوات من ملف JSON'

    def handle(self, *args, **options):
        data_path = os.path.join(settings.BASE_DIR, '..', 'importer', 'output', 'movies.json')
        
        if not os.path.exists(data_path):
            self.stdout.write(self.style.ERROR(f'❌ الملف غير موجود: {data_path}'))
            return

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for item in data:
            if 'stream_url' in item:
                obj, created = LiveStream.objects.get_or_create(
                    title=item['title'],
                    defaults={
                        'thumbnail': item.get('thumbnail', ''),
                        'stream_url': item['stream_url'],
                        'is_public': item.get('is_public', True),
                        'is_active': item.get('is_active', True),
                        'country': item.get('country', ''),
                        'description': item.get('description', ''),
                    }
                )
                if created:
                    count += 1

        self.stdout.write(
            self.style.SUCCESS(f'✅ تم إضافة {count} قناة جديدة بنجاح!')
        )