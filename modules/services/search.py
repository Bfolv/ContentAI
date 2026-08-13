from modules.utils.logger import logger
from modules.services.youtube_client import YouTubeClient

class SearchService:

    def __init__(self):
        self.youtube = YouTubeClient()

    def buscar_por_nicho(self, nicho, quantidade=5):
        logger.info("Buscando vídeos...")
        return self.youtube.buscar_videos(
            termo=nicho,
            quantidade=quantidade
        )