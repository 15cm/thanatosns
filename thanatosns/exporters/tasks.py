from celery import shared_task
from ninja.schema import Schema
import posts
from posts.models import Post
from .models import PostExportStatus
from django.db.models import Q
from datetime import datetime
import logging
from celery import Task
from django.utils import timezone

logger = logging.getLogger(__name__)

MEDIA_EXPORTER_ID = "media_exporter"


# TODO: implement the export function.
def export_medias(post: Post):
    print(f"Exporting post {post.id}")


class ExportTaskState(Schema):
    total_count: int = 0
    exported_count: int = 0
    failed_count: int = 0


# TODO: add single task heartbeat locking.
@shared_task(bind=True)
def export_medias_task(self: Task):
    task_state = ExportTaskState()
    posts_to_export = Post.objects.prefetch_related("export_status").filter(
        Q(export_status__isnull=True)
        | (
            Q(export_status__exporter_id=MEDIA_EXPORTER_ID)
            & Q(export_status__is_exported=False)
        )
    )
    task_state.total_count = posts_to_export.count()
    export_statuses = []
    for post in posts_to_export:
        export_status: PostExportStatus
        if post.export_status.all().count() == 0:
            export_status = PostExportStatus.objects.create(
                exporter_id=MEDIA_EXPORTER_ID,
                is_exported=False,
                post=post,
            )
        else:
            export_status = post.export_status.all()[0]
        try:
            export_medias(post)
        except Exception as e:
            logger.error(e)
            task_state.failed_count += 1
            self.update_state(state="PROGRESS", meta=task_state.dict())
            continue
        task_state.exported_count += 1
        self.update_state(state="PROGRESS", meta=task_state.dict())
        export_status.is_exported = True
        export_status.exported_at = timezone.now()
        export_statuses.append(export_status)

    PostExportStatus.objects.bulk_update(
        export_statuses, ["is_exported", "exported_at"]
    )
