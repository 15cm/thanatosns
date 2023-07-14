from pathlib import Path
from unittest import mock
from django.conf import settings
from export.exporters.base_exporter import ExportResult
from export.exporters.media_exporter import (
    MediaExporter,
    MEDIA_EXPORTER_ID,
    MediaExporterOptions,
)
from export.models import PostExportStatus
from posts.models import Post
import pytest
from posts.test_utils import create_post_from_model_payload
import requests_mock


@pytest.fixture
def media_exporter(fs_patched):
    return MediaExporter(MediaExporterOptions(disable_exif_population=True))


@pytest.fixture
def unexported_post(db):
    Post.objects.create()


@pytest.fixture
def post_model_payload_1():
    return {
        "id": 1,
        "url": "https://twitter/1/status/1",
        "platform": "twitter",
        "title": "hello",
        "body": "world",
        "published_at": "2023-07-04T08:19:28.114Z",
        "medias": [
            {
                "id": 1,
                "url": "https://pbs.twimg.com/media/1",
                "index": 0,
            },
            {
                "id": 2,
                "url": "https://pbs.twimg.com/media/2",
                "index": 1,
            },
        ],
        "author": {
            "id": 1,
            "handle": "abc",
            "names": ["Jack"],
            "urls": ["https://twitter/1"],
        },
    }


def create_mock_response(
    status=200,
    content="CONTENT",
    content_type="application/json",
    json_data=None,
    raise_for_status=None,
):
    mock_resp = mock.Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = mock.Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content
    mock_resp.headers["content-type"] = content_type
    # add json data if provided
    if json_data:
        mock_resp.json = mock.Mock(return_value=json_data)
    return mock_resp


@pytest.fixture
def post_1(db, post_model_payload_1):
    return create_post_from_model_payload(post_model_payload_1)


@pytest.fixture
def response_jpeg():
    return create_mock_response(content_type="image/jpeg")


@pytest.mark.django_db
def test_export(fs_patched, media_exporter: MediaExporter, post_1: Post):
    with requests_mock.Mocker() as m:
        m.get(
            "https://pbs.twimg.com/media/1",
            headers={"content-type": "image/jpeg"},
            content=b"CONTENT",
        )
        m.get(
            "https://pbs.twimg.com/media/2",
            headers={"content-type": "image/png"},
            content=b"CONTENT",
        )
        result: ExportResult
        try:
            result = media_exporter.export(post_1)
        except Exception as e:
            assert False, f"Should not raise exception {e}"
    assert Path(
        f"{settings.THANATOSNS_EXPORT_DIR}/{media_exporter.exporter_id}/2023/07/04/post_1/media_0_id_1.jpg"
    ).exists()
    assert Path(
        f"{settings.THANATOSNS_EXPORT_DIR}/{media_exporter.exporter_id}/2023/07/04/post_1/media_1_id_2.png"
    ).exists()
    assert (
        Post.objects.get(id=1)
        .export_statuses.filter(exporter_id=media_exporter.exporter_id)
        .first()
        .is_exported
    )
