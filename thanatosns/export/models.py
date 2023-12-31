from django.db import models

from posts.models import Post


class PostExportStatus(models.Model):
    exporter_id = models.CharField(max_length=255)
    is_exported = models.BooleanField()
    export_path = models.CharField(max_length=255)
    exported_at = models.DateTimeField(null=True, blank=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="export_statuses"
    )

    class Meta:
        verbose_name_plural = "Post export statuses"
        constraints = [
            models.UniqueConstraint(
                name="unique_exporter_per_post", fields=["exporter_id", "post"]
            )
        ]
