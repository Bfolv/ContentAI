from pathlib import Path

from modules.services.search import SearchService
from modules.services.upload import UploadService
from modules.analyzers.score_analyzer import ScoreAnalyzer
from modules.download.youtube_downloader import YouTubeDownloader
from modules.utils.history import carregar_historico, salvar_video

from config import MIN_SCORE_DOWNLOAD


def main():

    # Inicializa os módulos principais do sistema.
    search = SearchService()
    analyzer = ScoreAnalyzer()
    downloader = YouTubeDownloader()
    uploader = UploadService()

    # Carrega todos os vídeos já processados anteriormente.
    historico = carregar_historico()

    # Busca vídeos de um determinado nicho.
    videos = search.buscar_por_nicho(
        nicho="curiosidades",
        quantidade=30
    )

    print(f"\n{len(videos)} vídeos encontrados.\n")

    # Analisa todos os vídeos encontrados.
    for video in videos:

        # Ignora vídeos que já foram processados anteriormente.
        if video.video_id in historico:

            print("=" * 60)
            print(video.titulo)
            print("Vídeo já foi processado anteriormente. Ignorado.")

            continue

        # Ignora vídeos maiores que 120 segundos.
        if video.duracao > 120:

            print("=" * 60)
            print(video.titulo)
            print(f"Duração: {video.duracao} segundos")
            print("Vídeo muito longo. Ignorado.")

            continue

        # Calcula a pontuação do vídeo.
        score = analyzer.calcular(video)

        print("=" * 60)
        print(video)
        print(f"Score: {score}")

        # Só continua se o vídeo atingir a pontuação mínima.
        if score < MIN_SCORE_DOWNLOAD:

            print("Score insuficiente. Vídeo ignorado.")

            continue

        print("Download autorizado.")

        # Baixa o vídeo.
        caminho = downloader.baixar_video(video.url)

        if not caminho:

            print("Erro durante o download.")
            continue

        video.caminho_download = caminho
        video.status = "baixado"

        print("Download concluído.")

        # Envia o vídeo para o YouTube.
        try:

            video_id_youtube = uploader.enviar_video(
                caminho_video=caminho,
                titulo=video.titulo,
                descricao=video.descricao,
                privacidade="public"
            )

        except Exception as erro:

            # Se o upload falhar, o arquivo NÃO será apagado
            # e o vídeo NÃO será registrado no histórico.
            print("Erro durante o upload.")
            print(f"Detalhes: {erro}")

            continue

        # Só chegamos aqui se o YouTube confirmou o upload.
        video.status = "publicado"

        print("Vídeo publicado com sucesso!")
        print(f"ID do vídeo no YouTube: {video_id_youtube}")

        # Registra o vídeo no histórico somente após a publicação.
        salvar_video(video.video_id)
        historico.add(video.video_id)

        # Remove o arquivo local somente após o upload confirmado.
        try:

            Path(caminho).unlink()

            print("Arquivo local excluído.")

        except OSError as erro:

            # Caso a exclusão falhe, o vídeo continua publicado.
            print("Não foi possível excluir o arquivo local.")
            print(f"Detalhes: {erro}")

    print("\nProcesso finalizado.")


if __name__ == "__main__":
    main()