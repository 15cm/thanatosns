from .base_exporter import BaseExporter
from posts.models import Post
import time


class MediaExporter(BaseExporter):
    def _process_one(self, post: Post):
        time.sleep(5)
        print(f"Exporting post {post.id}")
