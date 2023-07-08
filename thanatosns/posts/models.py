from enum import unique
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex


class Post(models.Model):
    url = models.CharField(max_length=255, unique=True)
    # The social platform of this post
    platform = models.CharField(max_length=255)
    title = models.TextField()
    body = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    # An author should only be null when the author is explicitly deleted.
    author = models.ForeignKey(
        "Author", related_name="posts", null=True, on_delete=models.SET_NULL
    )


class Media(models.Model):
    url = models.CharField(max_length=255)
    index = models.PositiveIntegerField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="medias")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_media_per_post", fields=["url", "index", "post"]
            )
        ]


class Author(models.Model):
    name = models.CharField(max_length=255)
    # TODO: Support author profiles to use the fields below.
    other_names = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    urls = ArrayField(models.CharField(max_length=255), null=True, blank=True)

    class Meta:
        indexes = [GinIndex(fields=["other_names"])]
