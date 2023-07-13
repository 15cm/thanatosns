from urllib.parse import urlencode
from typing import Any
from ninja.testing.client import TestClient
from posts import models
from posts.views import PostOut, router
from django.db import models
import pytest
from ninja.testing.client import TestClient, TestAsyncClient
from asgiref.sync import sync_to_async, async_to_sync
import decorator
from posts.models import Post
from .test_utils import create_post_from_model_payload


def async_test(func):
    def inner(func, *args, **kwargs):
        return async_to_sync(func)(*args, **kwargs)

    return decorator.decorator(inner, func)


@pytest.fixture
def client():
    # A hack to make sync and async paths work together in a router for testing. The path operation object is shard for the same path.
    for _, path_operation in router.path_operations.items():
        path_operation.is_async = False
    return TestClient(router)


@pytest.fixture
def async_client():
    # A hack to make sync and async paths work together in a router for testing. The path operation object is shard for the same path.
    for _, path_operation in router.path_operations.items():
        path_operation.is_async = True
    return TestAsyncClient(router)


def filter_out_keys_from_dict(dict_in: dict[str, Any], keys: set[str]):
    dict_out: dict[str, Any] = {}
    for k, v in dict_in.items():
        if k not in keys:
            if isinstance(v, dict):
                dict_out[k] = filter_out_keys_from_dict(v, keys)
            if isinstance(v, list):
                dict_out[k] = [
                    filter_out_keys_from_dict(ele, keys)
                    if isinstance(ele, dict)
                    else ele
                    for ele in v
                ]
            else:
                dict_out[k] = v
    return dict_out


def merge_dict_to_model(payload: dict[str, Any], obj: models.Model):
    for attr, value in payload.items():
        setattr(obj, attr, value)


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


@pytest.fixture
def post_1(db, post_model_payload_1):
    return create_post_from_model_payload(post_model_payload_1)


@pytest.fixture
def post_create_payload_1(post_model_payload_1: dict[str, Any]):
    return filter_out_keys_from_dict(post_model_payload_1, {"id"})


@async_test
@pytest.mark.django_db(transaction=True, reset_sequences=True)
async def test_create(
    async_client: TestAsyncClient, post_model_payload_1, post_create_payload_1
):
    create_repsonse = await async_client.post(f"/", json=post_create_payload_1)
    assert create_repsonse.status_code == 200
    assert create_repsonse.json() == {"id": 1}
    assert await sync_to_async(PostOut.from_orm)(
        await Post.objects.aget(id=1)
    ) == PostOut(
        **{
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
    )


@async_test
@pytest.mark.django_db
async def test_get(async_client: TestAsyncClient, post_1):
    get_repsonse = await async_client.get(f"/1")
    assert get_repsonse.status_code == 200
    assert get_repsonse.json() == {
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


@pytest.mark.django_db
def test_list(client: TestClient, post_1):
    list_repsonse = client.get(f"/")
    assert list_repsonse.status_code == 200
    assert list_repsonse.json() == {
        "count": 1,
        "items": [
            {
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
        ],
    }


@pytest.mark.django_db
def test_list_filter_found(client: TestClient, post_1):
    list_repsonse = client.get("/", request_params={"search": "hello"})
    assert list_repsonse.status_code == 200
    assert list_repsonse.json() == {
        "count": 1,
        "items": [
            {
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
        ],
    }


@pytest.mark.django_db
def test_list_filter_not_found(client: TestClient, post_1):
    list_repsonse = client.get("/?" + urlencode({"search": "unmatched"}))
    assert list_repsonse.status_code == 200
    assert list_repsonse.json() == {
        "count": 0,
        "items": [],
    }


@async_test
@pytest.mark.django_db
async def test_delete(async_client: TestAsyncClient, post_1):
    delete_repsonse = await async_client.delete("/1")
    assert delete_repsonse.status_code == 200
    assert delete_repsonse.json() == {"success": True}
    assert await Post.objects.filter(id=1).afirst() == None
