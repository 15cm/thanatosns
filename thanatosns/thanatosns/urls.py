from django.contrib import admin
from django.urls import path
from posts.views import api as posts_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", posts_api.urls),
]
