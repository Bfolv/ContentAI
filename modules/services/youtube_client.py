from googleapiclient.discovery import build

from modules.utils.time_utils import converter_duracao_para_segundos
from config import YOUTUBE_API_KEY
from modules.models.video import Video


class YouTubeClient:

    def __init__(self):
        # Cria a conexão com a API do YouTube.
        self.youtube = build(
            "youtube",
            "v3",
            developerKey=YOUTUBE_API_KEY
        )

    def buscar_videos(self, termo, quantidade=5):
        """
        Pesquisa vídeos no YouTube e retorna
        uma lista de objetos Video.
        """

        request = self.youtube.search().list(
            part="snippet",
            q=termo,
            type="video",
            maxResults=quantidade
        )

        response = request.execute()

        # Guarda apenas os IDs retornados pela pesquisa.
        video_ids = []

        for item in response["items"]:
            video_ids.append(item["id"]["videoId"])

        # Converte a lista em uma string separada por vírgulas,
        # formato exigido pela API videos.list().
        video_ids = ",".join(video_ids)

        # Busca informações completas dos vídeos encontrados.
        request = self.youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_ids
        )
        

        video_details = request.execute()
        print(video_details["items"][0])

        # Lista que armazenará os objetos Video.
        videos = []

        # Percorre os detalhes completos dos vídeos.
        for item in video_details["items"]:

            snippet = item["snippet"]
            statistics = item.get("statistics", {})
            content = item.get("contentDetails", {})

            video = Video(

                video_id=item["id"],

                titulo=snippet["title"],

                descricao=snippet["description"],

                canal=snippet["channelTitle"],

                thumbnail=snippet["thumbnails"]["default"]["url"],

                url=f"https://www.youtube.com/watch?v={item['id']}",

                duracao=converter_duracao_para_segundos(content.get("duration", "PT0S")),

                views=int(statistics.get("viewCount", 0)),

                likes=int(statistics.get("likeCount", 0)),

                comentarios=int(statistics.get("commentCount", 0)),

                idioma=snippet.get("defaultLanguage", "desconhecido"),

                qualidade=content.get("definition", "desconhecida")

            )

            videos.append(video)

        return videos