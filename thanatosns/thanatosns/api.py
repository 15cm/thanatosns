from ninja import NinjaAPI
from posts.views import routers as posts_routers

api = NinjaAPI()

for router in posts_routers:
    api.add_router("/posts/", router)
