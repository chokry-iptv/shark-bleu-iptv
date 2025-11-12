from django.contrib import admin
from .models import Movie, Series, Episode, Genre, Subscription, LiveStream


# ================================
# نماذج المحتوى العامة
# ================================

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'duration_minutes', 'is_public')
    list_filter = ('is_public', 'release_year', 'genres')
    search_fields = ('title', 'description')
    filter_horizontal = ('genres', 'allowed_subscriptions')
    list_per_page = 20


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'is_public')
    list_filter = ('is_public', 'release_year', 'genres')
    search_fields = ('title', 'description')
    filter_horizontal = ('genres', 'allowed_subscriptions')


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'series', 'season_number', 'episode_number', 'duration_minutes')
    list_filter = ('series', 'season_number')
    search_fields = ('title', 'series__title')
    ordering = ('series', 'season_number', 'episode_number')
    list_per_page = 30


@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_public', 'is_active')
    list_filter = ('is_public', 'is_active')
    search_fields = ('title', 'description')
    list_per_page = 20


# ================================
# نموذج الاشتراك (مع حماية الكود)
# ================================

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_code', 'is_active', 'expiry_date')
    list_filter = ('is_active', 'expiry_date')
    search_fields = ('user__username', 'access_code')
    
    # الحقول القابلة للتعديل عند الإنشاء/التعديل
    fields = ('user', 'is_active', 'expiry_date')
    
    # جعل كود الاشتراك للقراءة فقط (يظهر بعد الحفظ)
    readonly_fields = ('access_code',)

    def get_readonly_fields(self, request, obj=None):
        """إخفاء access_code كحقل إدخال، حتى في وضع التعديل."""
        if obj is None:  # كائن جديد
            return self.readonly_fields
        return self.readonly_fields  # كائن موجود