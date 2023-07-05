from ninja import Router
from .tasks import export_medias_task

router = Router()


@router.post("/medias")
def create_media_export(request):
    export_medias_task.delay()  # type: ignore
    return {"success": True}
