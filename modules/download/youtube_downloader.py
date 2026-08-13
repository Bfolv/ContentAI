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
        self.download_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def baixar_video(self, url: str) -> str:
        """
        Baixa um vídeo utilizando o yt-dlp.

        O ID do vídeo é incluído no nome do arquivo.

        Exemplo:

        [wUbXZFuHicE] O desespero do PT.mp4

        Isso permite que o RecoveryService identifique
        posteriormente qual vídeo pertence a cada arquivo.

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

            # O ID do vídeo será armazenado no nome do arquivo.
            #
            # Exemplo:
            # [ABC123] Meu vídeo.mp4
            "outtmpl": str(
                self.download_path /
                "[%(id)s] %(title)s.%(ext)s"
            ),

            # Junta vídeo e áudio automaticamente.
            "merge_output_format": "mp4",

            # Não imprime dezenas de mensagens no terminal.
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:

            # Faz o download.
            info = ydl.extract_info(
                url,
                download=True
            )

            # Descobre o caminho gerado pelo yt-dlp.
            arquivo = Path(
                ydl.prepare_filename(info)
            )

            # Como configuramos merge_output_format="mp4",
            # o arquivo final será .mp4 quando houver
            # necessidade de juntar vídeo + áudio.
            #
            # Ajustamos o caminho retornado para refletir
            # o arquivo final.
            if arquivo.suffix.lower() != ".mp4":

                arquivo = arquivo.with_suffix(".mp4")

        return str(arquivo)