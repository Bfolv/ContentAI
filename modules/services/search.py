from modules.utils.logger import logger
from modules.services.youtube_client import YouTubeClient


class SearchService:

    def __init__(self):

        self.youtube = YouTubeClient()

    def buscar_por_nicho(
        self,
        nicho,
        quantidade=5,
        modo="shorts"
    ):
        """
        Busca vídeos de acordo com o tipo de conteúdo.

        modos disponíveis:

            shorts
                Busca vídeos classificados pelo YouTube
                como curtos e limita o resultado a vídeos
                de até 180 segundos.

            longos
                Futuramente será utilizado pelo pipeline
                responsável por vídeos longos e edição.

        Por enquanto, o modo "longos" não será utilizado
        pelo ContentAI.
        """

        logger.info(
            f"Buscando vídeos | nicho={nicho} | modo={modo}"
        )

        return self.youtube.buscar_videos(
            termo=nicho,
            quantidade=quantidade,
            modo=modo
        )