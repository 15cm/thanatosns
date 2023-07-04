from typing import Optional
from django.db.models.query import Prefetch
from ninja import NinjaAPI
from ninja import ModelSchema, Query
from django.db import transaction
from ninja import FilterSchema, Field
from ninja.pagination import paginate

from posts.models import Author, Media, MediaContentTypeChoices, Post
from django.shortcuts import get_object_or_404


api = NinjaAPI()


class AuthorIn(ModelSchema):
    class Config:
        model = Author
        model_fields = ["name"]


class MediaIn(ModelSchema):
    content_type: MediaContentTypeChoices

    class Config:
        model = Media
        model_exclude = ["post"]


class PostIn(ModelSchema):
    medias: list[MediaIn]
    authors: list[AuthorIn]

    class Config:
        model = Post
        model_exclude = ["authors"]


class AuthorOut(ModelSchema):
    class Config:
        model = Author
        model_fields = ["name"]


class MediaOut(ModelSchema):
    content_type: MediaContentTypeChoices

    class Config:
        model = Media
        model_exclude = ["post"]


class PostOut(ModelSchema):
    medias: list[MediaOut]
    authors: list[AuthorOut]

    class Config:
        model = Post
        model_exclude = ["authors"]


@api.post("/posts")
def create_post(request, payload: PostIn):
    payload_dict = payload.dict()
    media_payloads = payload_dict.pop("medias")
    author_payloads = payload_dict.pop("authors")
    post = Post.objects.create(**payload_dict)
    with transaction.atomic():
        for media_payload in media_payloads:
            media = Media.objects.create(**media_payload, post=post)
        for author_payload in author_payloads:
            (author, _) = Author.objects.get_or_create(name=author_payload["name"])
            post.authors.add(author)
    return {"url": post.url}


@api.get("/posts/{post_id}", response=PostOut)
def get_post(request, post_id: int):
    return get_object_or_404(
        Post.objects.prefetch_related(
            Prefetch("medias", queryset=Media.objects.order_by("index")),
            Prefetch("authors", queryset=Author.objects.order_by("name")),
        ),
        id=post_id,
    )


class PostFilterSchema(FilterSchema):
    url: Optional[str]
    platform: Optional[str]
    search: Optional[str] = Field(q=["title__icontains", "body__icontains"])
    author_name: Optional[str] = Field(q=["authors__name__icontains"])


@api.get("/posts", response=list[PostOut])
@paginate
def list_post(request, filters: PostFilterSchema = Query(...)):
    posts = Post.objects.all()
    return filters.filter(posts)
