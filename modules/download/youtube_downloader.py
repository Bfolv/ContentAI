from pathlib import Path
from yt_dlp import YoutubeDL


class YouTubeDownloader:
    """
    Responsável exclusivamente pelo download de vídeos.

    Esta classe não conhece a API do YouTube,
    não faz buscas e não edita vídeos.

    Sua única responsabilidade é receber uma URL
    e salvar o vídeo na pasta de downloads.
    """

    def __init__(self):

        # Define a pasta onde os vídeos originais serão armazenados.
        self.download_path = Path("downloads/originais")

        # Caso a pasta não exista, ela será criada automaticamente.
        self.download_path.mkdir(parents=True, exist_ok=True)

    def baixar_video(self, url: str) -> str:
        """
        Baixa um vídeo utilizando o yt-dlp.

        Args:
            url (str):
                URL completa do vídeo.

        Returns:
            str:
                Caminho completo do arquivo salvo.
        """

        ydl_opts = {

            # Melhor vídeo + melhor áudio disponíveis.
            "format": "bestvideo+bestaudio/best",

            # Nome do arquivo.
            "outtmpl": str(self.download_path / "%(title)s.%(ext)s"),

            # Junta vídeo e áudio automaticamente.
            "merge_output_format": "mp4",

            # Não imprime dezenas de mensagens no terminal.
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:

            # Faz o download.
            info = ydl.extract_info(url, download=True)

            # Descobre o caminho final do arquivo.
            arquivo = ydl.prepare_filename(info)

        return arquivo