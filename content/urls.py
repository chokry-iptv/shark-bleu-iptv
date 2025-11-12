# content/urls.py
from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.home, name='home'),
    path('access/', views.access_view, name='access'),
    path('profile/', views.subscriber_profile, name='profile'),
    path('logout/', views.subscriber_logout, name='logout'),
    path('movie/<int:movie_id>/', views.watch_movie, name='watch_movie'),
    path('series/<int:series_id>/', views.series_detail, name='series_detail'),
    path('episode/<int:episode_id>/', views.watch_episode, name='watch_episode'),
    path('live/', views.live_streams, name='live_streams'),
    path('live/<int:stream_id>/', views.watch_live, name='watch_live'),
    
    # 👇 المسار الجديد (أضف هذا السطر)
    path('create-admin/', views.create_admin, name='create_admin'),
    
    # Debug (للتطوير فقط)
    path('debug/', views.debug_movies, name='debug_movies'),
]