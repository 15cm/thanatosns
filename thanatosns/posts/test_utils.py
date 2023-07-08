import copy
from typing import Any, Optional
from .models import Post, Media, Author


def create_post_from_model_payload(model_payload: dict[str, Any]) -> Post:
    payload = copy.deepcopy(model_payload)
    media_payloads: list[dict[str, Any]] = []
    author_payload: Optional[dict[str, Any]] = None
    if "medias" in payload:
        media_payloads = payload.pop("medias")
    if "author" in payload:
        author_payload = payload.pop("author")

    post = Post.objects.create(**payload)
    for media_payload in media_payloads:
        Media.objects.create(**media_payload, post=post)
    if author_payload:
        author = Author.objects.create(**author_payload)
        post.author = author
    post.save()
    return post
