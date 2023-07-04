from typing import Any
import copy
from urllib.parse import urlencode
from ninja.testing.client import TestClient
from posts import models
from posts.views import PostOut, router
from django.db import models
import pytest
from ninja.testing.client import TestClient, TestAsyncClient
from asgiref.sync import sync_to_async, async_to_sync
import decorator
from posts.models import Post, Media, Author
from django.db import transaction
from annoying.functions import get_object_or_None


def async_test(func):
    def inner(func, *args, **kwargs):
        return async_to_sync(func)(*args, **kwargs)

    return decorator.decorator(inner, func)


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def async_client():
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


@sync_to_async
@transaction.atomic()
def create_post_from_model_payload(model_payload: dict[str, Any]):
    payload = copy.deepcopy(model_payload)
    media_payloads: list[dict[str, Any]] = []
    author_payloads: list[dict[str, Any]] = []
    if "medias" in payload:
        media_payloads = payload.pop("medias")
    if "authors" in payload:
        author_payloads = payload.pop("authors")

    post = get_object_or_None(Post, id=payload["id"])
    if not post:
        post = Post.objects.create(**payload)
    else:
        merge_dict_to_model(payload, post)
        post.save()

    for media_payload in media_payloads:
        media = get_object_or_None(Media, id=payload["id"])
        if not media:
            media = Media.objects.create(**media_payload, post=post)
        else:
            merge_dict_to_model(media_payload, media)
            media.post = post
            media.save()
    for author_payload in author_payloads:
        author = get_object_or_None(Author, id=payload["id"])
        if not author:
            author = Author.objects.create(**author_payload)
        else:
            merge_dict_to_model(author_payload, author)
            author.save()
        author.posts.add(post)


@pytest.fixture
def post_model_payload_1():
    return {
        "id": 1,
        "url": "https://twitter/1",
        "platform": "twitter",
        "title": "hello",
        "body": "world",
        "published_at": "2023-07-04T08:19:28.114Z",
        "medias": [
            {
                "id": 1,
                "url": "https://pbs.twimg.com/media/1",
                "index": 0,
                "content_type": "IMAGE",
            },
            {
                "id": 2,
                "url": "https://pbs.twimg.com/media/2",
                "index": 1,
                "content_type": "IMAGE",
            },
        ],
        "authors": [
            {
                "id": 1,
                "name": "John",
            }
        ],
    }


@pytest.fixture
def post_create_payload_1(post_model_payload_1: dict[str, Any]):
    return filter_out_keys_from_dict(post_model_payload_1, {"id"})


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@async_test
async def test_create(
    async_client: TestAsyncClient, post_model_payload_1, post_create_payload_1
):
    create_repsonse = await async_client.post(f"/", json=post_create_payload_1)
    assert create_repsonse.status_code == 200
    assert create_repsonse.json() == {"id": post_model_payload_1["id"]}
    assert await sync_to_async(PostOut.from_orm)(
        await Post.objects.aget(id=post_model_payload_1["id"])
    ) == PostOut(**post_model_payload_1)


@pytest.mark.django_db()
@async_test
async def test_get(async_client: TestAsyncClient, post_model_payload_1):
    await create_post_from_model_payload(post_model_payload_1)

    get_repsonse = await async_client.get(f"/1")
    assert get_repsonse.status_code == 200
    assert get_repsonse.json() == post_model_payload_1


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_list(client: TestClient, payload):
    create_response = client.post(f"/", json=payload)
    assert create_response.status_code == 200
    assert create_response.json() == {"id": 1}

    list_repsonse = client.get(f"/")
    assert list_repsonse.status_code == 200
    assert list_repsonse.json() == {
        "count": 1,
        "items": [
            {
                "id": 1,
                "url": "https://twitter/1",
                "platform": "twitter",
                "title": "hello",
                "body": "world",
                "published_at": "2023-07-04T08:19:28.114Z",
                "medias": [
                    {
                        "id": 1,
                        "url": "https://pbs.twimg.com/media/1",
                        "index": 0,
                        "content_type": "IMAGE",
                    },
                    {
                        "id": 2,
                        "url": "https://pbs.twimg.com/media/2",
                        "index": 1,
                        "content_type": "IMAGE",
                    },
                ],
                "authors": [{"id": 1, "name": "John"}],
            }
        ],
    }


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_list_filter_found(client: TestClient, payload):
    create_response = client.post(f"/", json=payload)
    assert create_response.status_code == 200
    assert create_response.json() == {"id": 1}

    list_repsonse = client.get("/", request_params={"search": "hello"})
    assert list_repsonse.status_code == 200
    assert list_repsonse.json() == {
        "count": 1,
        "items": [
            {
                "id": 1,
                "url": "https://twitter/1",
                "platform": "twitter",
                "title": "hello",
                "body": "world",
                "published_at": "2023-07-04T08:19:28.114Z",
                "medias": [
                    {
                        "id": 1,
                        "url": "https://pbs.twimg.com/media/1",
                        "index": 0,
                        "content_type": "IMAGE",
                    },
                    {
                        "id": 2,
                        "url": "https://pbs.twimg.com/media/2",
                        "index": 1,
                        "content_type": "IMAGE",
                    },
                ],
                "authors": [{"id": 1, "name": "John"}],
            }
        ],
    }


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_list_filter_not_found(client: TestClient, payload):
    create_response = client.post(f"/", json=payload)
    assert create_response.status_code == 200
    assert create_response.json() == {"id": 1}

    list_repsonse = client.get("/?" + urlencode({"search": "unmatched"}))
    assert list_repsonse.status_code == 200
    assert list_repsonse.json() == {
        "count": 0,
        "items": [],
    }


@pytest.mark.django_db()
@async_test
async def test_delete(async_client: TestAsyncClient, post_model_payload_1):
    await create_post_from_model_payload(post_model_payload_1)

    delete_repsonse = await async_client.delete("/1")
    assert delete_repsonse.status_code == 200
    assert delete_repsonse.json() == {"success": True}
    assert await Post.objects.filter(id=post_model_payload_1["id"]).afirst() == None
