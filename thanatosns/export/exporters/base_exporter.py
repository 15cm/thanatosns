from abc import abstractmethod
import os
from pathlib import Path
from typing import Iterable, Optional
from django.conf import settings
from django.utils import timezone
from export.models import PostExportStatus

from posts.models import Post
from ninja.schema import Schema
import logging

logger = logging.getLogger(__name__)


class ExportResult(Schema):
    export_path: str


class BaseExporter:
    exporter_id: str
    root_dir: Path

    def __init__(self, exporter_id: str) -> None:
        self.exporter_id = exporter_id
        self.root_dir = Path(settings.THANATOSNS_EXPORT_DIR) / self.exporter_id

    def export(self, post: Post):
        self.root_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(self.root_dir, os.W_OK):
            raise PermissionError(f"No write access to {self.root_dir}")
        self._process(post)
        export_statuses = list(post.export_statuses.all())
        export_status: PostExportStatus
        if len(export_statuses) == 0:
            export_status = PostExportStatus.objects.create(
                exporter_id=self.exporter_id,
                is_exported=False,
                post=post,
            )
        else:
            export_status = export_statuses[0]
        export_path = self._export_path(post).as_posix()
        export_status.is_exported = True
        export_status.exported_at = timezone.now()
        export_status.export_path = export_path
        export_status.save()
        return ExportResult(export_path=export_path)

    @abstractmethod
    def _process(self, post: Post):
        pass

    @abstractmethod
    def _export_path(self, post: Post) -> Path:
        pass
