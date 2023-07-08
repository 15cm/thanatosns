import mimetypes
from pathlib import Path
from typing import Optional

from django.conf import settings

import celery
from .base_exporter import BaseExporter
from posts.models import Media, Post
import requests

MEDIA_EXPORTER_ID = "media_exporter"


class UnsupportedContentTypeException(Exception):
    pass


class MediaProcessException(Exception):
    pass


class MediaExporter(BaseExporter):
    def __init__(self, task: celery.Task) -> None:
        super().__init__(MEDIA_EXPORTER_ID, task)

    def _process_one(self, post: Post):
        post_dir: Path = (
            self.root_dir / post.published_at.strftime("%Y/%m/%d") / f"post_{post.id}"
        )
        post_dir.mkdir(parents=True, exist_ok=True)
        media: Media
        err_urls: list[str] = []
        last_exception: Optional[Exception] = None
        for media in post.medias.all():
            response = requests.get(media.url)
            try:
                response.raise_for_status()
                content_type = response.headers["content-type"]
                if content_type not in settings.THANATOSNS_MEDIA_CONTENT_TYPES:
                    raise UnsupportedContentTypeException(
                        f"content-type={content_type}"
                    )
                extension = mimetypes.guess_extension(content_type)
                media_path = post_dir / f"media_{media.index}_id_{media.id}{extension}"
                with open(media_path, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                err_urls.append(media.url)
                last_exception = e
        if last_exception:
            raise MediaProcessException(f"for urls: {err_urls}") from last_exception
