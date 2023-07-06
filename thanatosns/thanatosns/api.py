from ninja import NinjaAPI
from posts.views import router as posts_router
from exporters.views import router as exporters_router

api = NinjaAPI()

api.add_router("/posts/", posts_router)
api.add_router("/exporters/", exporters_router)
