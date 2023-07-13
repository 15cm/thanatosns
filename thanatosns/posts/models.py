from enum import unique
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex


class PostManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .defer(
                "metadata",
            )
        )


class Post(models.Model):
    url = models.CharField(max_length=255, unique=True)
    # The social platform of this post
    platform = models.CharField(max_length=255)
    title = models.TextField()
    body = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    # Any metadata of the post that is not supported for now.
    metadata = models.JSONField(null=True, blank=True)
    # An author should only be null when the author is explicitly deleted.
    author = models.ForeignKey(
        "Author", related_name="posts", null=True, on_delete=models.SET_NULL
    )

    objects = PostManager()


class Media(models.Model):
    url = models.CharField(max_length=255)
    index = models.PositiveIntegerField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="medias")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_media_per_post", fields=["index", "post"]
            )
        ]


class Author(models.Model):
    handle = models.CharField(max_length=255, unique=True)
    names = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    urls = ArrayField(models.CharField(max_length=255), null=True, blank=True)

    class Meta:
        indexes = [GinIndex(fields=["names"])]
