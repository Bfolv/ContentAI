from modules.providers.base_provider import BaseProvider

class YouTubeAPIProvider(BaseProvider):

    def buscar_videos(self, nicho, quantidade):
        videos = []
        for i in range(quantidade):
            videos.append({
                "titulo": f"Vídeo {i + 1} sobre {nicho}",
                "url": f"https://youtube.com/video{i + 1}"
            })

        return videos
        