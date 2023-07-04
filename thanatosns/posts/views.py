from ninja import NinjaAPI
from ninja import ModelSchema
from datetime import datetime

from posts.models import Author, Media, Post

api = NinjaAPI()


class AuthorIn(ModelSchema):
    class Config:
        model = Author
        model_fields = ["name"]


class MediaIn(ModelSchema):
    class Config:
        model = Media
        model_exclude = ["post"]


class PostIn(ModelSchema):
    medias: list[MediaIn]
    authors: list[AuthorIn]

    class Config:
        model = Post
        model_exclude = ["authors"]


@api.post("/posts")
def create_post(request, payload: PostIn):
    payload_dict = payload.dict()
    author_payloads = payload_dict.pop("authors")
    post = Post.objects.create(**payload_dict)
    for author_payload in author_payloads:
        (author, _) = Author.objects.get_or_create(name=author_payload["name"])
        post.authors.add(author)
    return {"url": post.url}


@api.get("/posts/{post_id}")
def get_post(request, post_id: int):
    pass
