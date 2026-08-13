from pathlib import Path
import re

from modules.services.youtube_client import YouTubeClient
from modules.utils.history import carregar_historico


class RecoveryService:
    """
    Responsável por recuperar vídeos que foram baixados
    mas ainda não foram publicados.

    O RecoveryService procura arquivos dentro de:

        downloads/originais/

    A partir do nome do arquivo, identifica o video_id,
    consulta os dados atuais do vídeo na API do YouTube
    e reconstrói o objeto Video.
    """

    def __init__(self):

        # Pasta onde os vídeos originais são armazenados.
        self.download_path = Path(
            "downloads/originais"
        )

        # Cliente responsável pela comunicação
        # com a API do YouTube.
        self.youtube = YouTubeClient()

    def encontrar_videos(self):
        """
        Procura arquivos que podem ser recuperados.

        Returns:
            list:
                Lista de objetos Video recuperados.
        """

        historico = carregar_historico()

        videos_recuperados = []

        # Caso a pasta ainda não exista.
        if not self.download_path.exists():

            return videos_recuperados

        print(
            "\nProcurando vídeos para recuperação..."
        )

        # Percorre todos os arquivos da pasta.
        for arquivo in self.download_path.iterdir():

            # Ignora diretórios.
            if not arquivo.is_file():
                continue

            # --------------------------------------------------
            # EXTRAÇÃO DO VIDEO_ID
            # --------------------------------------------------

            video_id = self._extrair_video_id(
                arquivo.name
            )

            # Se não conseguimos identificar o ID,
            # não podemos recuperar automaticamente.
            if not video_id:

                print(
                    "\nArquivo ignorado:"
                )

                print(
                    f"Nome: {arquivo.name}"
                )

                print(
                    "Não foi possível identificar "
                    "o ID do vídeo."
                )

                continue

            # --------------------------------------------------
            # HISTÓRICO
            # --------------------------------------------------

            # Se já foi publicado/processado,
            # não deve voltar para a fila.
            if video_id in historico:

                print(
                    "\nArquivo já registrado "
                    "no histórico."
                )

                print(
                    f"ID: {video_id}"
                )

                continue

            # --------------------------------------------------
            # BUSCA NA API
            # --------------------------------------------------

            print(
                f"\nRecuperando vídeo: {video_id}"
            )

            try:

                video = self.youtube.buscar_video_por_id(
                    video_id
                )

            except Exception as erro:

                print(
                    "Erro ao consultar o vídeo "
                    "na API do YouTube."
                )

                print(
                    f"Detalhes: {erro}"
                )

                continue

            # --------------------------------------------------
            # VÍDEO NÃO ENCONTRADO
            # --------------------------------------------------

            if video is None:

                print(
                    "Vídeo não encontrado na API."
                )

                print(
                    f"ID: {video_id}"
                )

                # Não apagamos o arquivo.
                continue

            # --------------------------------------------------
            # ASSOCIA O ARQUIVO LOCAL AO VIDEO
            # --------------------------------------------------

            video.caminho_download = str(
                arquivo
            )

            video.status = "pendente"

            videos_recuperados.append(
                video
            )

            print(
                "Vídeo recuperado com sucesso."
            )

        return videos_recuperados

    def _extrair_video_id(self, nome_arquivo):
        """
        Extrai o ID do YouTube do nome do arquivo.

        Formato esperado:

            [VIDEO_ID] Título do vídeo.mp4

        Exemplo:

            [BW0Ni50UOVE] As descobertas mais
            impressionantes da história.mp4

        Returns:
            str | None
        """

        resultado = re.match(
            r"^\[([A-Za-z0-9_-]{11})\]",
            nome_arquivo
        )

        if not resultado:

            return None

        return resultado.group(1)