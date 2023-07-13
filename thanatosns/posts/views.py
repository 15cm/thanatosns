from typing import Optional
from django.db.models.query import Prefetch, QuerySet
from ninja import Router
from ninja import ModelSchema, Query
from django.db import transaction
from ninja import FilterSchema, Field
from ninja.pagination import paginate
from asgiref.sync import sync_to_async

from posts.models import Author, Media, Post
from django.shortcuts import get_object_or_404
from annoying.functions import get_object_or_None


router = Router()


@sync_to_async
def aget_object_or_404(*kargs, **kwargs):
    return get_object_or_404(*kargs, **kwargs)


class AuthorIn(ModelSchema):
    class Config:
        model = Author
        model_exclude = ["id"]


class MediaIn(ModelSchema):
    class Config:
        model = Media
        model_exclude = ["id", "post"]


class PostIn(ModelSchema):
    medias: list[MediaIn]
    author: AuthorIn
    metadata: Optional[dict] = None

    class Config:
        model = Post
        model_exclude = ["id"]


class AuthorOut(ModelSchema):
    class Config:
        model = Author
        model_fields = "__all__"


class MediaOut(ModelSchema):
    class Config:
        model = Media
        model_exclude = ["post"]


class PostOut(ModelSchema):
    medias: list[MediaOut]
    author: Optional[AuthorOut]

    class Config:
        model = Post
        model_exclude = ["metadata"]


@router.post(
    "/",
    description="Create a post. The author is identified by the `handle` field. Other author information is only honored when the author is first created.",
)
async def create_post(request, payload: PostIn):
    payload_dict = payload.dict()
    media_payloads = payload_dict.pop("medias")
    author_payload = payload_dict.pop("author")

    @sync_to_async
    @transaction.atomic()
    def create_object() -> Post:
        post = Post.objects.create(**payload_dict)
        for media_payload in media_payloads:
            media = Media.objects.create(**media_payload, post=post)
        author = get_object_or_None(Author, handle=author_payload["handle"])
        if author is None:
            author = Author.objects.create(**author_payload)
        post.author = author
        post.save()
        return post

    post = await create_object()
    return {"id": post.id}


def post_prefetch_relationships(qs: QuerySet[Post]) -> QuerySet[Post]:
    return qs.select_related("author").prefetch_related(
        Prefetch("medias", queryset=Media.objects.order_by("index"))
    )


@router.get("/{post_id}", response=PostOut)
async def get_post(request, post_id: int):
    return await aget_object_or_404(
        post_prefetch_relationships(Post.objects.all()),
        id=post_id,
    )


class PostFilterSchema(FilterSchema):
    url: Optional[str]
    platform: Optional[str]
    search: Optional[str] = Field(q=["title__icontains", "body__icontains"])
    author_name: Optional[str] = Field(q=["authors__name__icontains"])


@router.delete("/{post_id}")
async def delete_post(request, post_id: int):
    await Post.objects.filter(id=post_id).adelete()
    return {"success": True}


@router.get("/", response=list[PostOut])
# Paginate support is not ready for async yet. See https://github.com/vitalik/django-ninja/issues/547
@paginate
def list_post(request, filters: PostFilterSchema = Query(...)):
    q = filters.get_filter_expression()
    return post_prefetch_relationships(Post.objects.all()).filter(q)


# TODO: support updating posts
