from pathlib import Path

from modules.services.search import SearchService
from modules.services.upload import UploadService
from modules.analyzers.score_analyzer import ScoreAnalyzer
from modules.download.youtube_downloader import YouTubeDownloader
from modules.utils.history import carregar_historico, salvar_video
from modules.utils.queue import VideoQueue
from modules.services.recovery import RecoveryService

from config import MIN_SCORE_DOWNLOAD


def publicar_video(
    uploader,
    fila,
    item,
    historico
):
    """
    Tenta publicar um vídeo que já está registrado na fila.

    Retorna:
        True  -> publicação concluída
        False -> upload falhou
    """

    caminho = item["caminho_download"]

    print("=" * 60)
    print(f"Publicando: {item['titulo']}")

    # Verifica se o arquivo ainda existe.
    if not Path(caminho).exists():

        print("Arquivo do vídeo não foi encontrado.")
        print(f"Caminho: {caminho}")

        return False

    try:

        video_id_youtube = uploader.enviar_video(
            caminho_video=caminho,
            titulo=item["titulo"],
            descricao=item["descricao"],
            privacidade="public"
        )

    except Exception as erro:

        # O vídeo continua na fila.
        print("Erro durante o upload.")
        print(f"Detalhes: {erro}")

        return False

    print("Vídeo publicado com sucesso!")
    print(f"ID do vídeo no YouTube: {video_id_youtube}")

    # Primeiro registra como concluído.
    salvar_video(item["video_id"])
    historico.add(item["video_id"])

    # Depois remove da fila.
    fila.remover(item["video_id"])

    # Só depois de confirmar o upload removemos o arquivo.
    try:

        Path(caminho).unlink()

        print("Arquivo local excluído.")

    except OSError as erro:

        # O vídeo já foi publicado e removido da fila.
        # Portanto, uma falha aqui não deve fazê-lo voltar para a fila.
        print("Não foi possível excluir o arquivo local.")
        print(f"Detalhes: {erro}")

    return True


def processar_fila(
    uploader,
    fila,
    historico
):
    """
    Processa todos os vídeos atualmente presentes na fila.

    Retorna:
        True  -> a fila estava vazia no final
        False -> ainda existem vídeos pendentes
    """

    if fila.vazia():

        print("Fila de publicação vazia.")

        return True

    print("\nVídeos pendentes encontrados na fila.")

    while not fila.vazia():

        item = fila.proximo()

        if item is None:
            break

        # Caso excepcional: evita tentar publicar algo
        # que já esteja registrado no histórico.
        if item["video_id"] in historico:

            print("=" * 60)
            print(item["titulo"])
            print("Vídeo já está no histórico. Removendo da fila.")

            fila.remover(item["video_id"])

            continue

        sucesso = publicar_video(
            uploader,
            fila,
            item,
            historico
        )

        # Se falhar, paramos aqui.
        #
        # O vídeo continua na fila e será tentado novamente
        # na próxima execução do ContentAI.
        if not sucesso:

            print(
                "\nUpload não concluído."
                "\nO vídeo continuará na fila."
            )

            return False

    print("\nFila processada com sucesso.")

    return True


def main():

    try:

        # ======================================================
        # INICIALIZAÇÃO DOS MÓDULOS
        # ======================================================

        search = SearchService()
        analyzer = ScoreAnalyzer()
        downloader = YouTubeDownloader()
        uploader = UploadService()
        fila = VideoQueue()
        recovery = RecoveryService()

        historico = carregar_historico()

        # ======================================================
        # 1. PRIMEIRO PROCESSAMOS A FILA EXISTENTE
        # ======================================================

        # ======================================================
        # RECUPERAÇÃO DE VÍDEOS ÓRFÃOS
        # ======================================================

        videos_recuperados = recovery.encontrar_videos()

        if videos_recuperados:

            print(
                f"\n{len(videos_recuperados)} vídeo(s) recuperado(s)."
            )

            for video in videos_recuperados:

                fila.adicionar(video)

                print(
                    f"Adicionado à fila: {video.titulo}"
                )

        # ======================================================
        # PROCESSAMENTO DA FILA
        # ======================================================

        fila_processada = processar_fila(
            uploader,
            fila,
            historico
        )

        # Se ainda existe um vídeo pendente porque houve erro,
        # não vamos baixar novos vídeos.
        if not fila_processada:

            print(
                "\nExistem vídeos pendentes na fila."
                "\nNovos downloads não serão realizados "
                "nesta execução."
            )

            return

        # ======================================================
        # 2. BUSCA DE NOVOS VÍDEOS
        # ======================================================

        videos = search.buscar_por_nicho(
            nicho="Curiosidades",
            quantidade=100
        )

        print(f"\n{len(videos)} vídeos encontrados.\n")

        # ======================================================
        # 3. PROCESSAMENTO DOS NOVOS VÍDEOS
        # ======================================================

        for video in videos:

            # --------------------------------------------------
            # Histórico
            # --------------------------------------------------

            if video.video_id in historico:

                print("=" * 60)
                print(video.titulo)
                print(
                    "Vídeo já foi processado anteriormente. "
                    "Ignorado."
                )

                continue

            # --------------------------------------------------
            # Duração
            # --------------------------------------------------

            if video.duracao > 180:

                print("=" * 60)
                print(video.titulo)
                print(
                    f"Duração: "
                    f"{video.duracao} segundos"
                )
                print("Vídeo muito longo. Ignorado.")

                continue

            # --------------------------------------------------
            # Score
            # --------------------------------------------------

            score = analyzer.calcular(video)

            print("=" * 60)
            print(video)
            print(f"Score: {score}")

            if score < MIN_SCORE_DOWNLOAD:

                print(
                    "Score insuficiente. "
                    "Vídeo ignorado."
                )

                continue

            # --------------------------------------------------
            # Download
            # --------------------------------------------------

            print("Download autorizado.")

            caminho = downloader.baixar_video(
                video.url
            )

            if not caminho:

                print("Erro durante o download.")

                continue

            video.caminho_download = caminho
            video.status = "baixado"

            print("Download concluído.")

            # --------------------------------------------------
            # ADICIONA À FILA ANTES DO UPLOAD
            # --------------------------------------------------

            fila.adicionar(video)

            print("Vídeo adicionado à fila.")

            # --------------------------------------------------
            # Upload
            # --------------------------------------------------

            item = fila.proximo()

            if item is None:

                print(
                    "Erro: vídeo não encontrado na fila."
                )

                continue

            sucesso = publicar_video(
                uploader,
                fila,
                item,
                historico
            )

            # --------------------------------------------------
            # Se falhar, paramos os novos downloads.
            # --------------------------------------------------

            if not sucesso:

                print(
                    "\nO upload falhou."
                    "\nO vídeo permanece na fila."
                    "\nNovos downloads serão interrompidos."
                )

                break

    finally:
        # ======================================================
        print("\nProcesso finalizado.")


if __name__ == "__main__":
    main()