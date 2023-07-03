from ninja import NinjaAPI
from ninja.schema import Schema
from datetime import datetime

from posts.models import Author, Post

api = NinjaAPI()


class AuthorIn(Schema):
    name: str


class PostIn(Schema):
    url: str
    platform: str
    title: str
    body: str
    published_at: datetime
    authors: list[AuthorIn]


@api.post("/posts")
def create_post(request, payload: PostIn):
    payload_dict = payload.dict()
    author_payloads = payload_dict.pop("authors")
    post = Post.objects.create(**payload_dict)
    for author_payload in author_payloads:
        (author, _) = Author.objects.get_or_create(name=author_payload["name"])
        post.authors.add(author)
    return {"url": post.url}
