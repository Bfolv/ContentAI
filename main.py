from modules.analyzers.score_analyzer import ScoreAnalyzer
from modules.download.youtube_downloader import YouTubeDownloader
from modules.services.active_profile import ActiveProfileService
from modules.services.content_pipeline import ContentPipelineService
from modules.services.recovery import RecoveryService
from modules.services.search import SearchService
from modules.services.upload import UploadService
from modules.utils.history import carregar_historico
from modules.utils.queue import VideoQueue


def main():

    try:

        # ======================================================
        # INICIALIZAÇÃO
        # ======================================================

        search = SearchService()
        analyzer = ScoreAnalyzer()
        downloader = YouTubeDownloader()
        uploader = UploadService()
        fila = VideoQueue()

        historico = carregar_historico()

        pipeline_service = ContentPipelineService(
            analyzer=analyzer,
            downloader=downloader,
            fila=fila,
            uploader=uploader,
            historico=historico,
        )

        # ======================================================
        # PERFIL ATIVO
        # ======================================================

        active_profile = ActiveProfileService()
        perfil = active_profile.obter()

        if perfil is None:
            print(
                "\nNão foi possível carregar "
                "o perfil ativo."
            )
            return

        print("\nPerfil ativo:")
        print(f"Nome: {perfil.nome}")
        print(f"Nicho: {perfil.nicho}")
        print(
            f"Tipo de conteúdo: "
            f"{perfil.tipo_conteudo}"
        )
        print(
            f"Score mínimo: "
            f"{perfil.min_score_download}"
        )

        # ======================================================
        # PIPELINE
        # ======================================================

        pipeline = pipeline_service.obter_pipeline(
            perfil.tipo_conteudo
        )

        if pipeline is None:
            print(
                f"\nTipo de conteúdo inválido: "
                f"{perfil.tipo_conteudo}"
            )
            return

        print(f"Pipeline selecionado: {pipeline}")

        # ======================================================
        # 1. RECUPERAÇÃO DE ARQUIVOS ÓRFÃOS
        # ======================================================

        recovery = RecoveryService()

        videos_recuperados = recovery.encontrar_videos()

        if videos_recuperados:

            print(
                f"\n{len(videos_recuperados)} "
                "vídeo(s) recuperado(s)."
            )

            for video in videos_recuperados:

                # A recuperação já verifica o histórico.
                # A fila também impede duplicações.
                fila.adicionar(video)

                print(
                    f"Vídeo recuperado e adicionado "
                    f"à fila: {video.titulo}"
                )

        # ======================================================
        # 2. PROCESSAMENTO DA FILA
        # ======================================================

        if not fila.vazia():

            sucesso = pipeline_service.processar_fila(
                perfil.tipo_conteudo
            )

            # Se um upload falhar, a fila permanece salva
            # e a execução termina sem iniciar novos downloads.
            if not sucesso:
                return

        # ======================================================
        # 3. BUSCA DE NOVOS VÍDEOS
        # ======================================================

        videos = search.buscar_por_nicho(
            nicho=perfil.nicho,
            quantidade=100,
            modo=perfil.tipo_conteudo,
        )

        print(
            f"\n{len(videos)} vídeos encontrados.\n"
        )

        # ======================================================
        # 4. EXECUÇÃO DO PIPELINE
        # ======================================================

        pipeline_service.executar(
            tipo_conteudo=perfil.tipo_conteudo,
            videos=videos,
            perfil=perfil,
        )

    except Exception as erro:

        print("\nErro durante a execução:")
        print(f"Detalhes: {erro}")

    finally:

        print("\nProcesso finalizado.")


if __name__ == "__main__":
    main()