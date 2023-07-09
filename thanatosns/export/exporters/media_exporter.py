import mimetypes
from pathlib import Path
from typing import Optional

from django.conf import settings

from .base_exporter import BaseExporter
from posts.models import Media, Post
import requests
from exiftool import ExifToolHelper

MEDIA_EXPORTER_ID = "media_exporter"


class UnsupportedContentTypeException(Exception):
    pass


class MediaProcessException(Exception):
    pass


def _populate_exif(path: Path, post: Post):
    with ExifToolHelper() as et:
        et.set_tags(
            [path],
            tags={
                "DateTimeOriginal": post.published_at.strftime("%Y:%m:%d %H:%M:%S%z"),
                "Title": post.title,
                "Subject": post.platform,
                "Description": post.body,
                "UserComment": post.url,
            }
            | ({"Artist": post.author} if post.author else {}),
            params=[
                "-P",
                "-overwrite_original",
                "-codedcharacterset=utf8",
                "-charset",
                "iptc=UTF8",
            ],
        )


class MediaExporter(BaseExporter):
    def __init__(self) -> None:
        super().__init__(MEDIA_EXPORTER_ID)

    def _process(self, post: Post):
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
                _populate_exif(media_path, post)
            except Exception as e:
                err_urls.append(media.url)
                last_exception = e
        if last_exception:
            raise MediaProcessException(
                f"Last error {last_exception}. For urls: {err_urls}"
            )
