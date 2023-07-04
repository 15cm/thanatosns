from ninja import NinjaAPI
from posts.views import router as posts_router

api = NinjaAPI()

api.add_router("/posts/", posts_router)
