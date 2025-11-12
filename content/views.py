from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.http import HttpResponse 
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.conf import settings
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .models import Movie, Series, Episode, LiveStream, Subscription


# ================================
# نظام الاشتراكات: تسجيل الدخول بكود
# ================================

def access_view(request):
    """صفحة إدخال كود الاشتراك."""
    if request.method == "POST":
        code = request.POST.get("access_code")
        try:
            subscription = Subscription.objects.get(access_code=code)
            if subscription.is_valid():
                user, created = User.objects.get_or_create(
                    username=f"sub_{subscription.id}",
                    defaults={"email": f"sub_{subscription.id}@temp.com"}
                )
                if created:
                    user.password = make_password(User.objects.make_random_password())
                    user.save()
                subscription.user = user
                subscription.save()
                login(request, user)
                return redirect("content:home")
            else:
                error = "هذا الكود غير نشط أو منتهي الصلاحية."
        except Subscription.DoesNotExist:
            error = "كود اشتراك غير صحيح."
        return render(request, "access.html", {"error": error})
    return render(request, "access.html")


# ================================
# تسجيل الخروج
# ================================

def subscriber_logout(request):
    """تسجيل خروج المشترك."""
    logout(request)
    return redirect("content:home")


# ================================
# الصفحة الرئيسية (عام + خاص + تصنيف القنوات حسب البلد)
# ================================

def home(request):
    """الصفحة الرئيسية: تعرض المحتوى العام والخاص (إذا كان المستخدم مسجلًا)."""
    movies_qs = Movie.objects.filter(is_public=True)
    series_qs = Series.objects.filter(is_public=True)
    live_streams_qs = LiveStream.objects.filter(is_public=True, is_active=True)

    if request.user.is_authenticated:
        try:
            sub = request.user.subscription
            if sub.is_valid():
                movies_qs = Movie.objects.filter(
                    models.Q(is_public=True) | models.Q(allowed_subscriptions=sub)
                ).distinct()
                series_qs = Series.objects.filter(
                    models.Q(is_public=True) | models.Q(allowed_subscriptions=sub)
                ).distinct()
                live_streams_qs = LiveStream.objects.filter(
                    models.Q(is_public=True, is_active=True) |
                    models.Q(allowed_subscriptions=sub, is_active=True)
                ).distinct()
        except Subscription.DoesNotExist:
            pass

    COUNTRY_ORDER = ["السعودية", "مصر", "المغرب", "الجزائر", "الإمارات"]
    all_countries = live_streams_qs.values_list('country', flat=True).distinct()
    grouped_streams = {}

    for country in COUNTRY_ORDER:
        if country in all_countries:
            grouped_streams[country] = live_streams_qs.filter(country=country)

    other_countries = set(all_countries) - set(COUNTRY_ORDER)
    if other_countries:
        grouped_streams["أخرى"] = live_streams_qs.filter(country__in=other_countries)

    return render(request, 'home.html', {
        'movies': movies_qs.order_by('-release_year')[:12],
        'series': series_qs.order_by('-release_year')[:12],
        'grouped_streams': grouped_streams,
    })


# ================================
# حماية الوصول إلى المحتوى
# ================================

def _check_access(request, obj):
    """تحقق من صلاحية الوصول إلى كائن (فيلم/مسلسل/قناة)."""
    if getattr(obj, 'is_public', False):
        return True
    if request.user.is_authenticated:
        try:
            sub = request.user.subscription
            if sub.is_valid() and obj.allowed_subscriptions.filter(id=sub.id).exists():
                return True
        except Subscription.DoesNotExist:
            pass
    return False


# ================================
# مشاهدة المحتوى
# ================================

def watch_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if not _check_access(request, movie):
        return redirect("content:access")
    return render(request, 'watch.html', {'movie': movie})


def series_detail(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    if not _check_access(request, series):
        return redirect("content:access")
    episodes = series.episodes.all().order_by('season_number', 'episode_number')
    return render(request, 'series_detail.html', {'series': series, 'episodes': episodes})


def watch_episode(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)
    if not _check_access(request, episode.series):
        return redirect("content:access")
    return render(request, 'watch_episode.html', {'episode': episode})


def live_streams(request):
    streams = LiveStream.objects.filter(is_public=True, is_active=True)
    if request.user.is_authenticated:
        try:
            sub = request.user.subscription
            if sub.is_valid():
                streams = LiveStream.objects.filter(
                    models.Q(is_public=True, is_active=True) |
                    models.Q(allowed_subscriptions=sub, is_active=True)
                ).distinct()
        except Subscription.DoesNotExist:
            pass
    return render(request, 'live_list.html', {'streams': streams})


def watch_live(request, stream_id):
    stream = get_object_or_404(LiveStream, id=stream_id, is_active=True)
    if not _check_access(request, stream):
        return redirect("content:access")
    return render(request, 'watch_live.html', {'stream': stream})


# ================================
# صفحة خاصة للمشتركين
# ================================

@login_required
def subscriber_profile(request):
    """صفحة خاصة تُعرض فقط للمشتركين المصادقين."""
    try:
        subscription = request.user.subscription
        if not subscription.is_valid():
            return render(request, 'profile.html', {
                'error': 'اشتراكك منتهي الصلاحية أو غير نشط.'
            })
    except Subscription.DoesNotExist:
        return redirect('content:access')

    movies = Movie.objects.filter(allowed_subscriptions=subscription)
    series = Series.objects.filter(allowed_subscriptions=subscription)
    live_streams = LiveStream.objects.filter(
        allowed_subscriptions=subscription, is_active=True
    )

    return render(request, 'profile.html', {
        'subscription': subscription,
        'movies': movies[:10],
        'series': series[:10],
        'live_streams': live_streams[:10],
    })



def create_admin(request):
    User = get_user_model()
    username = "admin"
    email = "admin@example.com"
    password = "SecurePass123!"  # ⚠️ غيّر هذا فور الدخول!
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        return HttpResponse(f"✅ تم إنشاء الحساب:<br>اسم المستخدم: {username}<br>كلمة المرور: {password}")
    return HttpResponse("⚠️ الحساب موجود مسبقًا")



# ================================
# Debug (للتطوير فقط)
# ================================

def debug_movies(request):
    if not settings.DEBUG:
        return JsonResponse({'error': 'Debug disabled in production.'}, status=403)
    data = list(Movie.objects.values('id', 'title', 'is_public', 'release_year'))
    return JsonResponse(data, safe=False)