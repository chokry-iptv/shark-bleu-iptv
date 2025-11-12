"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include  # ← أضف 'include' هنا

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('content.urls')),  # ← الآن سيعمل
]