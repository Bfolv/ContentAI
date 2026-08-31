from pathlib import Path

from modules.services.content_policy import ContentPolicyService
from modules.utils.history import salvar_video


class ShortsPipeline:
    """
    Pipeline responsável pelo processamento de Shorts.

    Fluxo:
        Policy → Duração → Score → Download → Fila → Upload
    """

    def __init__(
        self,
        analyzer,
        downloader,
        fila,
        uploader,
        historico
    ):
        self.analyzer = analyzer
        self.downloader = downloader
        self.fila = fila
        self.uploader = uploader
        self.historico = historico
        self.policy = ContentPolicyService()

    # ==========================================================
    # RECUPERAÇÃO DE DOWNLOADS
    # ==========================================================

    def processar_downloads_pendentes(self):
        """
        Tenta novamente downloads que falharam em uma execução
        anterior.

        Cada vídeo possui no máximo duas tentativas.
        """

        videos = self.fila.obter_downloads_pendentes()

        if not videos:
            return

        print(
            f"\n{len(videos)} download(s) pendente(s)."
        )

        for item in videos:

            tentativas = self.fila.obter_tentativas_download(
                item["video_id"]
            )

            # A primeira execução já realizou a tentativa 1.
            # Portanto, aqui só permitimos a tentativa 2.
            if tentativas >= 2:

                print("=" * 60)
                print(item["titulo"])
                print(
                    "Download falhou duas vezes. "
                    "Vídeo descartado."
                )

                self.fila.remover(
                    item["video_id"]
                )

                continue

            print("=" * 60)
            print(item["titulo"])
            print(
                "Tentando download novamente "
                f"({tentativas + 1}/2)..."
            )

            caminho = self.downloader.baixar_video(
                item["url"]
            )

            if not caminho:

                print(
                    "Segunda tentativa de download "
                    "falhou."
                )

                self.fila.remover(
                    item["video_id"]
                )

                print(
                    "Vídeo descartado após duas tentativas."
                )

                continue

            self.fila.atualizar_download(
                item["video_id"],
                caminho
            )

            print(
                "Download recuperado com sucesso."
            )

    # ==========================================================
    # FILA
    # ==========================================================

    def processar_fila(self):
        """
        Publica os vídeos prontos da fila.

        Downloads pendentes são tratados separadamente
        por processar_downloads_pendentes().
        """

        item = self.fila.proximo()

        if item is None:
            print("\nFila de publicação vazia.")
            return True

        print("\nIniciando processamento da fila...")

        while item is not None:

            if not self.publicar_video(item):

                print(
                    "\nO upload falhou."
                    "\nO vídeo permanece na fila."
                    "\nProcessamento interrompido."
                )

                return False

            item = self.fila.proximo()

        print("\nFila processada com sucesso.")

        return True

    # ==========================================================
    # PUBLICAÇÃO
    # ==========================================================

    def publicar_video(self, item):
        """
        Publica um vídeo da fila.

        A fila e o histórico só são alterados após
        confirmação de sucesso no upload.
        """

        caminho = item["caminho_download"]

        print("=" * 60)
        print(f"Publicando: {item['titulo']}")

        if not caminho or not Path(caminho).exists():

            print(
                "Arquivo do vídeo não foi encontrado."
            )

            print(
                f"Caminho: {caminho}"
            )

            return False

        try:

            video_id_youtube = self.uploader.enviar_video(
                caminho_video=caminho,
                titulo=item["titulo"],
                descricao=item["descricao"],
                privacidade="public",
            )

        except Exception as erro:

            print("Erro durante o upload.")
            print(f"Detalhes: {erro}")

            return False

        print(
            "Vídeo publicado com sucesso!"
        )

        print(
            f"ID do vídeo no YouTube: "
            f"{video_id_youtube}"
        )

        salvar_video(
            item["video_id"]
        )

        self.historico.add(
            item["video_id"]
        )

        self.fila.remover(
            item["video_id"]
        )

        try:

            Path(caminho).unlink()

            print(
                "Arquivo local excluído."
            )

        except OSError as erro:

            print(
                "Não foi possível excluir "
                "o arquivo local."
            )

            print(
                f"Detalhes: {erro}"
            )

        return True

    # ==========================================================
    # NOVOS VÍDEOS
    # ==========================================================

    def processar(self, videos, perfil):
        """
        Analisa e baixa novos vídeos.

        Downloads aprovados entram na fila.
        Downloads que falharem ficam registrados para
        uma nova tentativa na próxima execução.
        """

        for video in videos:

            # --------------------------------------------------
            # HISTÓRICO
            # --------------------------------------------------

            if video.video_id in self.historico:

                print("=" * 60)
                print(video.titulo)
                print(
                    "Vídeo já foi processado anteriormente. "
                    "Ignorado."
                )

                continue

            # --------------------------------------------------
            # POLÍTICA
            # --------------------------------------------------

            if not self.policy.pode_processar(
                perfil,
                video
            ):
                continue

            # --------------------------------------------------
            # DURAÇÃO
            # --------------------------------------------------

            if video.duracao > 180:

                print("=" * 60)
                print(video.titulo)
                print(
                    f"Duração: {video.duracao}s"
                )

                print(
                    "Vídeo acima de 180 segundos. "
                    "Ignorado pelo pipeline de Shorts."
                )

                continue

            # --------------------------------------------------
            # SCORE
            # --------------------------------------------------

            score = self.analyzer.calcular(
                video
            )

            print("=" * 60)
            print(video)
            print(f"Score: {score}")

            if score < perfil.min_score_download:

                print(
                    "Score insuficiente. "
                    "Vídeo ignorado."
                )

                continue

            # --------------------------------------------------
            # DOWNLOAD
            # --------------------------------------------------

            print(
                "Download autorizado."
            )

            try:

                caminho = self.downloader.baixar_video(
                    video.url
                )

            except Exception as erro:

                print(
                    "Erro durante o download."
                )

                print(
                    f"Detalhes: {erro}"
                )

                caminho = None

            if not caminho:

                print(
                    "Download falhou."
                )

                # A primeira falha é persistida.
                # A nova tentativa acontecerá somente
                # na próxima execução.
                self.fila.adicionar_download_pendente(
                    video
                )

                print(
                    "Download marcado para nova "
                    "tentativa na próxima execução."
                )

                continue

            video.caminho_download = caminho
            video.status = "baixado"

            print(
                "Download concluído."
            )

            # --------------------------------------------------
            # FILA
            # --------------------------------------------------

            self.fila.adicionar(
                video
            )

            print(
                "Vídeo adicionado à fila."
            )

        # Publica somente os downloads que foram
        # concluídos nesta execução.
        return self.processar_fila()