from ninja import NinjaAPI
from posts.views import routers as posts_routers
from exporters.views import router as exporters_router

api = NinjaAPI()

for router in posts_routers:
    api.add_router("/posts/", router)
api.add_router("/exporters/", exporters_router)
