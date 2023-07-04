from urllib.parse import urlencode
from ninja.testing.client import TestClient
from posts.views import router
import pytest
from ninja.testing.client import TestClient


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def payload():
    return {
        "url": "https://twitter/1",
        "platform": "twitter",
        "title": "hello",
        "body": "world",
        "published_at": "2023-07-04T08:19:28.114Z",
        "medias": [
            {
                "url": "https://pbs.twimg.com/media/1",
                "index": 0,
                "content_type": "IMAGE",
            },
            {
                "url": "https://pbs.twimg.com/media/2",
                "index": 1,
                "content_type": "IMAGE",
            },
        ],
        "authors": [{"name": "John"}],
    }


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_and_get(client: TestClient, payload):
    create_response = client.post(f"/", json=payload)
    assert create_response.status_code == 200
    assert create_response.json() == {"id": 1}

    get_repsonse = client.get(f"/1")
    assert get_repsonse.status_code == 200
    assert get_repsonse.json() == {
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


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_and_list(client: TestClient, payload):
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
def test_create_and_list_filter_found(client: TestClient, payload):
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
def test_create_and_list_filter_not_found(client: TestClient, payload):
    create_response = client.post(f"/", json=payload)
    assert create_response.status_code == 200
    assert create_response.json() == {"id": 1}

    list_repsonse = client.get("/?" + urlencode({"search": "unmatched"}))
    assert list_repsonse.status_code == 200
    assert list_repsonse.json() == {
        "count": 0,
        "items": [],
    }


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_and_delete(client: TestClient, payload):
    create_response = client.post(f"/", json=payload)
    assert create_response.status_code == 200
    assert create_response.json() == {"id": 1}

    delete_repsonse = client.delete("/1")
    assert delete_repsonse.status_code == 200
    assert delete_repsonse.json() == {"success": True}
