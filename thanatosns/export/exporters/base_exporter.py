from abc import abstractmethod
import os
from pathlib import Path
from typing import Iterable
from django.conf import settings
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
    root_dir: Path

    def __init__(self, exporter_id: str, task: celery.Task) -> None:
        self.exporter_id = exporter_id
        self.task = task
        self.task_state = ExportTaskState()
        self.root_dir = Path(settings.THANATOSNS_EXPORT_DIR) / self.exporter_id

    def process(self, posts: Iterable[Post]):
        self.root_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(self.root_dir, os.W_OK):
            raise PermissionError(f"No write access to {self.root_dir}")
        export_statuses = []
        for post in posts:
            self.task_state.total_count += 1
            export_status: PostExportStatus
            if post.export_statuses.all().count() == 0:
                export_status = PostExportStatus.objects.create(
                    exporter_id=self.exporter_id,
                    is_exported=False,
                    post=post,
                )
            else:
                export_status = post.export_statuses.all()[0]
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