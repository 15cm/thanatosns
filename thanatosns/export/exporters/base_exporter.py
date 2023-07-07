from abc import abstractmethod
from django.db.models.query import QuerySet
from django.utils import timezone
import celery
from export.models import PostExportStatus

from posts.models import Post
from ninja.schema import Schema
import logging
import posts


logger = logging.getLogger(__name__)


class ExportTaskState(Schema):
    total_count: int = 0
    exported_count: int = 0
    failed_count: int = 0


class BaseExporter:
    exporter_id: str
    task: celery.Task
    task_state: ExportTaskState

    def __init__(self, exporter_id: str, task: celery.Task) -> None:
        self.exporter_id = exporter_id
        self.task = task
        self.task_state = ExportTaskState()

    def process(self, posts: QuerySet[Post]):
        export_statuses = []
        self.task_state.total_count = posts.count()
        for post in posts:
            export_status: PostExportStatus
            if post.export_status.all().count() == 0:
                export_status = PostExportStatus.objects.create(
                    exporter_id=self.exporter_id,
                    is_exported=False,
                    post=post,
                )
            else:
                export_status = post.export_status.all()[0]
            try:
                self._process_one(post)
            except Exception as e:
                logger.error(e)
                self.task_state.failed_count += 1
                self.task.update_state(state="PROGRESS", meta=self.task_state.dict())
                continue
            self.task_state.exported_count += 1
            self.task.update_state(state="PROGRESS", meta=self.task_state.dict())
            export_status.is_exported = True
            export_status.exported_at = timezone.now()
            export_statuses.append(export_status)

        PostExportStatus.objects.bulk_update(
            export_statuses, ["is_exported", "exported_at"]
        )

    @abstractmethod
    def _process_one(self, post: Post):
        pass
