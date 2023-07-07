from ninja import NinjaAPI
from posts.views import router as posts_router
from export.views import router as export_router

api = NinjaAPI()

api.add_router("/posts/", posts_router)
api.add_router("/export/", export_router)
