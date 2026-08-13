import json
from pathlib import Path


class VideoQueue:
    """
    Gerencia a fila persistente de vídeos pendentes de publicação.

    A fila é armazenada em um arquivo JSON para que os vídeos
    não sejam perdidos quando o programa for encerrado.
    """

    def __init__(self):

        # Arquivo onde a fila será armazenada.
        self.queue_file = Path("downloads/fila.json")

        # Garante que a pasta downloads exista.
        self.queue_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def carregar(self):
        """
        Carrega os vídeos atualmente presentes na fila.

        Retorna:
            list:
                Lista de vídeos pendentes.
        """

        if not self.queue_file.exists():
            return []

        try:

            with open(
                self.queue_file,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(arquivo)

            if not isinstance(dados, list):
                return []

            return dados

        except (json.JSONDecodeError, OSError):

            return []

    def salvar(self, videos):
        """
        Salva a lista atual de vídeos na fila.
        """

        with open(
            self.queue_file,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                videos,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    def adicionar(self, video):
        """
        Adiciona um vídeo à fila.

        Evita duplicação através do video_id.
        """

        fila = self.carregar()

        for item in fila:

            if item["video_id"] == video.video_id:
                return

        fila.append(
            {
                "video_id": video.video_id,
                "titulo": video.titulo,
                "descricao": video.descricao,
                "url": video.url,
                "caminho_download": video.caminho_download,
                "status": "pendente"
            }
        )

        self.salvar(fila)

    def proximo(self):
        """
        Retorna o primeiro vídeo pendente da fila.

        Retorna:
            dict | None:
                Dados do próximo vídeo ou None se a fila estiver vazia.
        """

        fila = self.carregar()

        if not fila:
            return None

        return fila[0]

    def remover(self, video_id):
        """
        Remove um vídeo da fila utilizando seu ID.
        """

        fila = self.carregar()

        fila = [
            video
            for video in fila
            if video["video_id"] != video_id
        ]

        self.salvar(fila)

    def vazia(self):
        """
        Retorna True quando não existem vídeos pendentes.
        """

        return len(self.carregar()) == 0