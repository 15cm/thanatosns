from django.contrib import admin

from posts.models import Author, Media, Post

admin.site.register(Post)
admin.site.register(Media)
admin.site.register(Author)
