from celery import shared_task
from ninja.schema import Schema
from django.core.cache import cache
import posts
from posts.models import Post
from .models import PostExportStatus
from django.db.models import Q
from datetime import datetime
import logging
from celery import Task
from django.utils import timezone
import time
from . import lease

logger = logging.getLogger(__name__)

MEDIA_EXPORTER_ID = "media_exporter"
MEDIA_TASK_ID_NAME = f"{MEDIA_EXPORTER_ID}_task_id"
MEDIA_TASK_LEASE_NAME = f"{MEDIA_EXPORTER_ID}_task_lease"


# TODO: implement the export function.
def export_medias(post: Post):
    time.sleep(5)
    print(f"Exporting post {post.id}")


def export_medias_task_cleanup():
    lease.stop(MEDIA_TASK_LEASE_NAME)
    cache.delete(MEDIA_TASK_ID_NAME)


class ExportTaskState(Schema):
    total_count: int = 0
    exported_count: int = 0
    failed_count: int = 0


# The task should only be run with the lease is already acquired. It allows the task invoker to know if the lease can be acquire.
@shared_task(bind=True)
def export_medias_task(self: Task, export_all: bool):
    with lease.refresh_lease_until_done(MEDIA_TASK_LEASE_NAME):
        task_state = ExportTaskState()
        posts_to_export = Post.objects.prefetch_related("export_status")
        if not export_all:
            posts_to_export.filter(
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
    export_medias_task_cleanup()
