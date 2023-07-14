import mimetypes
from shutil import which
import os
from pathlib import Path
from typing import Optional

from django.conf import settings

from ninja.schema import Schema

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
            | ({"Artist": post.author.handle} if post.author else {}),
            params=[
                "-P",
                "-overwrite_original",
                "-codedcharacterset=utf8",
                "-charset",
                "iptc=UTF8",
            ],
        )


class MediaExporterOptions(Schema):
    disable_exif_population: bool = False
    disable_media_download: bool = False


class MediaExporter(BaseExporter):
    options: MediaExporterOptions

    def __init__(self, options: MediaExporterOptions) -> None:
        self.options = options
        super().__init__(MEDIA_EXPORTER_ID)

    def _export_path(self, post: Post) -> Path:
        return (
            self.root_dir / post.published_at.strftime("%Y/%m/%d") / f"post_{post.id}"
        )

    def _process(self, post: Post):
        post_dir = self._export_path(post)
        post_dir.mkdir(parents=True, exist_ok=True)
        media: Media
        err_urls: list[str] = []
        err_paths: list[str] = []
        last_exception: Optional[Exception] = None
        media_paths: list[Path] = []
        if not self.options.disable_media_download:
            for media in post.medias.all():
                try:
                    response = requests.get(media.url)
                    response.raise_for_status()
                    content_type = response.headers["content-type"]
                    if content_type not in settings.THANATOSNS_MEDIA_CONTENT_TYPES:
                        raise UnsupportedContentTypeException(
                            f"content-type={content_type}"
                        )
                    extension = mimetypes.guess_extension(content_type)
                    media_path = (
                        post_dir / f"media_{media.index}_id_{media.id}{extension}"
                    )
                    with open(media_path, "wb") as f:
                        f.write(response.content)
                    media_paths.append(media_path)
                except Exception as e:
                    err_urls.append(media.url)
                    last_exception = e
        elif export_status := post.export_statuses.filter(is_exported=True).first():
            export_path = export_status.export_path
            media_paths = [
                os.path.abspath(os.path.join(export_path, p))
                for p in os.listdir(export_path)
            ]
        for media_path in media_paths:
            try:
                if not self.options.disable_exif_population:
                    _populate_exif(media_path, post)
            except Exception as e:
                err_paths.append(media_path.as_posix())
                last_exception = e
        if last_exception:
            raise MediaProcessException(
                f"Last error {last_exception}. For urls: {err_urls}, for paths: {err_paths}"
            )
