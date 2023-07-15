from typing import Any
from celery import shared_task
from export.exporters.media_exporter import (
    MediaExporter,
    MediaExporterOptions,
)
from posts.models import Post
from django.db.models import Q


@shared_task
def export_medias_task(post_id: int, disable_media_download: bool) -> dict[str, Any]:
    media_exporter = MediaExporter(
        MediaExporterOptions(disable_media_download=disable_media_download)
    )
    post = Post.objects.get(id=post_id)
    return media_exporter.export(post).dict()
