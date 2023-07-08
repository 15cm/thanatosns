import copy
from typing import Any
from .models import Post, Media, Author


def create_post_from_model_payload(model_payload: dict[str, Any]) -> Post:
    payload = copy.deepcopy(model_payload)
    media_payloads: list[dict[str, Any]] = []
    author_payloads: list[dict[str, Any]] = []
    if "medias" in payload:
        media_payloads = payload.pop("medias")
    if "authors" in payload:
        author_payloads = payload.pop("authors")

    post = Post.objects.create(**payload)
    for media_payload in media_payloads:
        Media.objects.create(**media_payload, post=post)
    for author_payload in author_payloads:
        author = Author.objects.create(**author_payload)
        author.posts.add(post)
    return post
