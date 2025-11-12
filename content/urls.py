from django.urls import path
from django.conf import settings
from . import views

# تحديد application namespace (مطلوب لاستخدام {% url 'content:...' %})
app_name = 'content'

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.home, name='home'),

    # نظام الاشتراكات
    path('access/', views.access_view, name='access'),
    path('profile/', views.subscriber_profile, name='profile'),
    path('logout/', views.subscriber_logout, name='logout'),

    # الأفلام
    path('movie/<int:movie_id>/', views.watch_movie, name='watch_movie'),

    # المسلسلات والحلقات
    path('series/<int:series_id>/', views.series_detail, name='series_detail'),
    path('episode/<int:episode_id>/', views.watch_episode, name='watch_episode'),

    # البث المباشر
    path('live/', views.live_streams, name='live_streams'),
    path('live/<int:stream_id>/', views.watch_live, name='watch_live'),
]

# نقطة التصحيح: تعمل فقط في وضع التطوير (DEBUG=True)
if settings.DEBUG:
    urlpatterns += [
        path('debug/', views.debug_movies, name='debug_movies'),
    ]
path('create-admin/', views.create_admin, name='create_admin'),