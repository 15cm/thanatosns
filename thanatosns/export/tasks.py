from celery import shared_task
from django.core.cache import cache
from export.exporters.media_exporter import MediaExporter, MEDIA_EXPORTER_ID
from posts.models import Post
from django.db.models import Q
from celery import Task
from . import lease

MEDIA_TASK_ID_NAME = f"{MEDIA_EXPORTER_ID}_task_id"
MEDIA_TASK_LEASE_NAME = f"{MEDIA_EXPORTER_ID}_task_lease"


def export_medias_task_cleanup():
    lease.stop(MEDIA_TASK_LEASE_NAME)
    cache.delete(MEDIA_TASK_ID_NAME)


# The task should only be run with the lease is already acquired. It allows the task invoker to know if the lease can be acquire.
@shared_task(bind=True)
def export_medias_task(self: Task, export_all: bool):
    with lease.refresh_lease_until_done(MEDIA_TASK_LEASE_NAME):
        media_exporter = MediaExporter(MEDIA_EXPORTER_ID, self)
        posts_to_export = Post.objects.prefetch_related(
            "export_statuses"
        ).prefetch_related("medias")
        if not export_all:
            posts_to_export = posts_to_export.filter(
                Q(export_statuses__isnull=True)
                | (
                    Q(export_statuses__exporter_id=MEDIA_EXPORTER_ID)
                    & Q(export_statuses__is_exported=False)
                )
            )
        media_exporter.process(posts_to_export)

    export_medias_task_cleanup()
