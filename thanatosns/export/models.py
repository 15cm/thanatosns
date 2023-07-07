from django.db import models

from posts.models import Post


class PostExportStatus(models.Model):
    exporter_id = models.CharField(max_length=255)
    is_exported = models.BooleanField()
    exported_at = models.DateTimeField(null=True, blank=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="export_status"
    )

    class Meta:
        verbose_name_plural = "Post export statuses"
        unique_together = ("exporter_id", "post")
