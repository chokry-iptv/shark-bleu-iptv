from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    access_code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.access_code}"

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        return True


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.IntegerField()
    duration_minutes = models.IntegerField()
    thumbnail = models.URLField()
    video_url = models.URLField(help_text="رابط ملف .m3u8")
    genres = models.ManyToManyField(Genre, blank=True)
    allowed_subscriptions = models.ManyToManyField('Subscription', blank=True, related_name='allowed_movies')
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Series(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.IntegerField()
    thumbnail = models.URLField()
    genres = models.ManyToManyField(Genre, blank=True)
    allowed_subscriptions = models.ManyToManyField('Subscription', blank=True, related_name='allowed_series')
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Series"

    def __str__(self):
        return self.title


class Episode(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='episodes')
    title = models.CharField(max_length=200)
    season_number = models.PositiveIntegerField()
    episode_number = models.PositiveIntegerField()
    duration_minutes = models.IntegerField()
    video_url = models.URLField()
    release_date = models.DateField()

    class Meta:
        unique_together = ('series', 'season_number', 'episode_number')
        ordering = ['season_number', 'episode_number']

    def __str__(self):
        return f"{self.series.title} - S{self.season_number}E{self.episode_number}"


class LiveStream(models.Model):
    title = models.CharField(max_length=200, verbose_name="اسم القناة")
    description = models.TextField(blank=True, verbose_name="وصف")
    thumbnail = models.URLField(blank=True, verbose_name="رابط الصورة المصغرة")
    stream_url = models.URLField(help_text="رابط البث المباشر بصيغة .m3u8", verbose_name="رابط البث")
    is_public = models.BooleanField(default=True, verbose_name="عام؟")
    is_active = models.BooleanField(default=True, verbose_name="نشط؟")
    country = models.CharField(max_length=50, blank=True, verbose_name="البلد")  # ← جديد
    
    
    allowed_subscriptions = models.ManyToManyField(
        'Subscription',
        blank=True,
        related_name='allowed_live_streams',
        verbose_name="الاشتراكات المسموح لها"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "بث مباشر"
        verbose_name_plural = "البث المباشر"