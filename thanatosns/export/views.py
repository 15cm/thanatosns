from ninja import Router
from ninja.schema import Schema
from .tasks import (
    export_medias_task,
    MEDIA_TASK_ID_NAME,
    MEDIA_TASK_LEASE_NAME,
    export_medias_task_cleanup,
)
from . import lease
from django.core.cache import cache
from thanatosns.celery import app as celery_app

router = Router()


class StartMediaExportIn(Schema):
    # Export medias for exported posts as well.
    export_all: bool = False


class StartMediaExportOut(Schema):
    # Status code 200: returns the id of the started task.
    # Status code 409: returns the id of the task that is still running
    task_id: str


class DetailResponse(Schema):
    detail: str


# Only one export can run at a time.
@router.post("/media", response={200: StartMediaExportOut, 409: StartMediaExportOut})
def start_media_export(request, payload: StartMediaExportIn):
    if not lease.acquire(MEDIA_TASK_LEASE_NAME):
        return 409, StartMediaExportOut(
            task_id=cache.get(MEDIA_TASK_ID_NAME, "unknown")
        )
    res = export_medias_task.delay(**payload.dict())  # type: ignore
    cache.set(MEDIA_TASK_ID_NAME, res.id)
    return StartMediaExportOut(task_id=res.id)


@router.delete("/media/{task_id}", response={200: DetailResponse, 404: DetailResponse})
def delete_media_export(request, task_id: str):
    if (task_id := cache.get(MEDIA_TASK_ID_NAME, None)) and lease.is_valid(
        MEDIA_TASK_LEASE_NAME
    ):
        celery_app.control.revoke(task_id, terminate=True)
        export_medias_task_cleanup()
        return DetailResponse(detail=f"Succeeded.")
    else:
        return 404, DetailResponse(detail="Task not found or its lease expired.")
