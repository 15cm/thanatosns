import threading

from django.http.response import HttpResponse
from ninja import Router
from ninja.errors import HttpError
from ninja.schema import Schema
from .tasks import (
    export_medias_task,
)
from .exporters.media_exporter import MEDIA_EXPORTER_ID
from . import lease
from django.core.cache import cache
from thanatosns.celery import app as celery_app
import celery
from posts.models import Post
from celery.result import AsyncResult
from django.db.models import Q

router = Router()

MEDIA_TASK_ID_NAME = f"{MEDIA_EXPORTER_ID}_task_id"
MEDIA_TASK_LEASE_NAME = f"{MEDIA_EXPORTER_ID}_task_lease"


class StartMediaExportIn(Schema):
    # Export medias for exported posts as well.
    export_all: bool = False


def background_media_export_cleanup():
    lease.release(MEDIA_TASK_LEASE_NAME)
    cache.delete(MEDIA_TASK_ID_NAME)


def background_media_export(input: StartMediaExportIn):
    with lease.refresh_lease_until_done(MEDIA_TASK_LEASE_NAME):
        posts_to_export = Post.objects.prefetch_related(
            "export_statuses"
        ).prefetch_related("medias")
        if not input.export_all:
            posts_to_export = posts_to_export.filter(
                Q(export_statuses__isnull=True)
                | (
                    Q(export_statuses__exporter_id=MEDIA_EXPORTER_ID)
                    & Q(export_statuses__is_exported=False)
                )
            )
        task_group = celery.group(
            [
                export_medias_task.s(post_id)
                for post_id in posts_to_export.values_list("id", flat=True)
            ]
        )
        result = task_group.apply_async()
        cache.set(MEDIA_TASK_ID_NAME, result.id)
        result.join()
    background_media_export_cleanup()


# Only one export can run at a time.
@router.post("/media")
def start_media_export_task(request, payload: StartMediaExportIn):
    if not lease.acquire(MEDIA_TASK_LEASE_NAME):
        raise HttpError(409, "The current media export task is still running.")
    background_thread = threading.Thread(
        target=background_media_export, args=(payload,), daemon=True
    )
    background_thread.start()


@router.delete("/media/{task_id}")
def delete_media_export_task(request, task_id: str):
    celery_app.control.revoke(task_id, terminate=True)


@router.delete("/media")
def delete_all_media_export_task(request):
    task_ids = []
    inspect = celery_app.control.inspect()
    for insepct_result in [inspect.active(), inspect.reserved()]:
        for _, tasks in insepct_result.items():
            for task in tasks:
                if task.name == "export.tasks.export_medias_task":
                    task_ids.append(task["id"])
    for task_id in task_ids:
        celery_app.control.revoke(task_id, terminate=True)
