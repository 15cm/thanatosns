from typing import Any, Iterable
from celery import shared_task
from django.core.cache import cache
from export.exporters.base_exporter import ProcessResult
from export.exporters.media_exporter import MediaExporter, MEDIA_EXPORTER_ID
from posts.models import Post
from django.db.models import Q
from celery import Task
from . import lease


@shared_task
def export_medias_task(post_id: int) -> dict[str, Any]:
    media_exporter = MediaExporter()
    post = Post.objects.get(id=post_id)
    return media_exporter.export(post).dict()
