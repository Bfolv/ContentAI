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

    def buscar_video_por_id(self, video_id: str):
        """
        Busca um vídeo específico pelo seu ID.

        Utilizado principalmente pelo RecoveryService,
        quando encontramos um arquivo local que precisa
        ser recuperado para a fila.

        Args:
            video_id (str):
                ID do vídeo no YouTube.

        Returns:
            Video | None:
                Objeto Video completo caso encontrado.
                None caso o vídeo não exista ou não esteja
                disponível.
        """

        resultado = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        ).execute()

        itens = resultado.get("items", [])

        if not itens:
            return None

        item = itens[0]

        snippet = item.get(
            "snippet",
            {}
        )

        content_details = item.get(
            "contentDetails",
            {}
        )

        statistics = item.get(
            "statistics",
            {}
        )

        # ======================================================
        # DURAÇÃO
        # ======================================================

        duracao = converter_duracao_para_segundos(
            content_details.get(
                "duration",
                "PT0S"
            )
        )

        # ======================================================
        # DADOS DO VÍDEO
        # ======================================================

        return Video(

            video_id=item["id"],

            titulo=snippet.get(
                "title",
                ""
            ),

            descricao=snippet.get(
                "description",
                ""
            ),

            canal=snippet.get(
                "channelTitle",
                ""
            ),

            thumbnail=snippet.get(
                "thumbnails",
                {}
            ).get(
                "default",
                {}
            ).get(
                "url",
                ""
            ),

            url=f"https://www.youtube.com/watch?v={item['id']}",

            duracao=duracao,

            views=int(
                statistics.get(
                    "viewCount",
                    0
                )
            ),

            likes=int(
                statistics.get(
                    "likeCount",
                    0
                )
            ),

            comentarios=int(
                statistics.get(
                    "commentCount",
                    0
                )
            ),

            idioma=snippet.get(
                "defaultLanguage",
                snippet.get(
                    "defaultAudioLanguage",
                    "desconhecido"
                )
            ),

            qualidade=content_details.get(
                "definition",
                "desconhecida"
            )
        )

    def buscar_videos(self,termo,quantidade=5,modo="shorts"):

        """
        Pesquisa vídeos no YouTube e retorna uma lista
        de objetos Video.

        modos:

            shorts
                Pesquisa vídeos classificados como curtos
                e mantém somente vídeos com até 180 segundos.

            longos
                Pesquisa vídeos classificados como longos.
                Será utilizado futuramente pelo sistema
                de edição e cortes.
        """

        # ======================================================
        # CONFIGURAÇÃO DO FILTRO DE DURAÇÃO
        # ======================================================

        if modo == "shorts":

            video_duration = "short"

        elif modo == "longos":

            video_duration = "long"

        else:

            raise ValueError(
                f"Modo de busca inválido: {modo}"
            )

        # ======================================================
        # PESQUISA
        # ======================================================

        request = self.youtube.search().list(
            part="snippet",
            q=termo,
            type="video",
            videoDuration=video_duration,
            maxResults=quantidade
        )

        response = request.execute()

        # ======================================================
        # IDs ENCONTRADOS
        # ======================================================

        video_ids = []

        for item in response.get("items", []):

            video_id = item.get(
                "id",
                {}
            ).get(
                "videoId"
            )

            if video_id:

                video_ids.append(
                    video_id
                )

        # Nenhum vídeo encontrado.
        if not video_ids:

            return []

        # ======================================================
        # BUSCA DOS DETALHES
        # ======================================================

        video_ids_string = ",".join(
            video_ids
        )

        request = self.youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_ids_string
        )

        video_details = request.execute()

        # ======================================================
        # CONSTRUÇÃO DOS OBJETOS VIDEO
        # ======================================================

        videos = []

        for item in video_details.get("items", []):

            snippet = item.get(
                "snippet",
                {}
            )

            statistics = item.get(
                "statistics",
                {}
            )

            content = item.get(
                "contentDetails",
                {}
            )

            duracao = converter_duracao_para_segundos(
                content.get(
                    "duration",
                    "PT0S"
                )
            )

            # ==================================================
            # REGRA EXATA DOS SHORTS
            # ==================================================
            #
            # A API possui apenas categorias de duração.
            #
            # Nossa regra de negócio é:
            #
            #       <= 180 segundos
            #
            # Portanto fazemos a validação novamente aqui.

            if modo == "shorts" and duracao > 180:

                continue

            # Para o futuro pipeline de vídeos longos,
            # só consideramos vídeos acima de 180 segundos.

            if modo == "longos" and duracao <= 180:

                continue

            video = Video(

                video_id=item["id"],

                titulo=snippet.get(
                    "title",
                    ""
                ),

                descricao=snippet.get(
                    "description",
                    ""
                ),

                canal=snippet.get(
                    "channelTitle",
                    ""
                ),

                thumbnail=snippet.get(
                    "thumbnails",
                    {}
                ).get(
                    "default",
                    {}
                ).get(
                    "url",
                    ""
                ),

                url=(
                    f"https://www.youtube.com/watch?v="
                    f"{item['id']}"
                ),

                duracao=duracao,

                views=int(
                    statistics.get(
                        "viewCount",
                        0
                    )
                ),

                likes=int(
                    statistics.get(
                        "likeCount",
                        0
                    )
                ),

                comentarios=int(
                    statistics.get(
                        "commentCount",
                        0
                    )
                ),

                idioma=snippet.get(
                    "defaultLanguage",
                    "desconhecido"
                ),

                qualidade=content.get(
                    "definition",
                    "desconhecida"
                )

            )

            videos.append(
                video
            )

        return videos