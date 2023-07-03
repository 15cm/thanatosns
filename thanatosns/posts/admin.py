from django.contrib import admin

from posts.models import Author, Post

admin.site.register(Post)
admin.site.register(Author)
