from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex


class Post(models.Model):
    url = models.CharField(max_length=255, primary_key=True)
    # The social platform of this post. Lowercase only.
    platform = models.CharField(max_length=255)
    title = models.TextField()
    body = models.TextField()
    published_at = models.DateTimeField()
    # one to many -> Media
    authors = models.ManyToManyField("Author")


class MediaContentTypeChoices(TextChoices):
    IMAGE = "IMAGE", _("Image")
    VIDEO = "VIDEO", _("Video")


class Media(models.Model):
    url = models.CharField(max_length=255, primary_key=True)
    index = models.IntegerField()
    content_type = models.CharField(
        max_length=63, choices=MediaContentTypeChoices.choices
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("url", "index")


class Author(models.Model):
    name = models.CharField(max_length=255)
    other_names = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    urls = ArrayField(models.CharField(max_length=255), null=True, blank=True)

    class Meta:
        indexes = [GinIndex(fields=["other_names"])]