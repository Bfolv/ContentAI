from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


class YouTubeDownloader:
    """
    Responsável exclusivamente pelo download de vídeos.
    """

    def __init__(self):

        self.download_path = Path(
            "downloads/originais"
        )

        self.download_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def baixar_video(self, url: str) -> str | None:
        """
        Baixa um vídeo utilizando o yt-dlp.

        Retorna o caminho do arquivo quando o download
        é concluído com sucesso ou None em caso de falha.
        """

        ydl_opts = {
            "format": "18/best[protocol=https][ext=mp4]/best",

            "outtmpl": str(
                self.download_path /
                "[%(id)s] %(title)s.%(ext)s"
            ),

            "merge_output_format": "mp4",

            "no_plugin_dirs": True,

            "quiet": True,
        }

        try:

            with YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(
                    url,
                    download=True
                )

                arquivo = Path(
                    ydl.prepare_filename(info)
                )

                # O yt-dlp pode gerar um arquivo temporário
                # e finalizar a extensão como .mp4 após o merge.
                if arquivo.suffix.lower() != ".mp4":
                    arquivo = arquivo.with_suffix(".mp4")

                if not arquivo.exists():

                    print(
                        "Download concluído, "
                        "mas o arquivo não foi encontrado."
                    )

                    return None

                return str(arquivo)

        except DownloadError as erro:

            print(
                "\nFalha ao baixar o vídeo."
            )
            print(f"URL: {url}")
            print(f"Detalhes: {erro}")

            return None

        except Exception as erro:

            print(
                "\nErro inesperado durante o download."
            )
            print(f"URL: {url}")
            print(f"Detalhes: {erro}")

            return None