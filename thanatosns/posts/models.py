from enum import unique
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex


class Post(models.Model):
    url = models.CharField(max_length=255, unique=True)
    # The social platform of this post
    platform = models.CharField(max_length=255)
    title = models.TextField()
    body = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    # one to many -> Media
    authors = models.ManyToManyField("Author", related_name="posts")


class MediaContentTypeChoices(TextChoices):
    IMAGE = "IMAGE", _("Image")
    VIDEO = "VIDEO", _("Video")


class Media(models.Model):
    url = models.CharField(max_length=255, unique=True)
    index = models.PositiveIntegerField()
    content_type = models.CharField(
        max_length=63, choices=MediaContentTypeChoices.choices
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="medias")

    class Meta:
        unique_together = ("url", "index")


class Author(models.Model):
    name = models.CharField(max_length=255)
    # TODO: Support author profiles to use the fields below.
    other_names = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    urls = ArrayField(models.CharField(max_length=255), null=True, blank=True)

    class Meta:
        indexes = [GinIndex(fields=["other_names"])]
