import json
from pathlib import Path


class VideoQueue:
    """
    Gerencia a fila persistente de vídeos pendentes.

    A fila é armazenada em JSON para que vídeos pendentes
    não sejam perdidos quando o programa for encerrado.
    """

    def __init__(self):

        self.queue_file = Path(
            "downloads/fila.json"
        )

        self.queue_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def carregar(self):
        """
        Carrega os vídeos presentes na fila.
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

            return dados if isinstance(dados, list) else []

        except (json.JSONDecodeError, OSError):

            return []

    def salvar(self, videos):
        """
        Salva a fila atual.
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
        Adiciona um vídeo pronto para publicação.

        Evita duplicação pelo video_id.
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
                "status": "pendente",
                "tentativas_download": 0
            }
        )

        self.salvar(fila)

    def adicionar_download_pendente(self, video):
        """
        Registra um vídeo cujo download falhou.

        A primeira falha já conta como uma tentativa.
        """

        fila = self.carregar()

        for item in fila:

            if item["video_id"] == video.video_id:

                item["tentativas_download"] = (
                    item.get("tentativas_download", 0) + 1
                )

                item["status"] = "download_pendente"

                self.salvar(fila)

                return

        fila.append(
            {
                "video_id": video.video_id,
                "titulo": video.titulo,
                "descricao": video.descricao,
                "url": video.url,
                "caminho_download": None,
                "status": "download_pendente",
                "tentativas_download": 1
            }
        )

        self.salvar(fila)

    def obter_downloads_pendentes(self):
        """
        Retorna somente vídeos que precisam de uma nova
        tentativa de download.
        """

        return [
            item
            for item in self.carregar()
            if item.get("status") == "download_pendente"
        ]

    def atualizar_download(self, video_id, caminho):
        """
        Marca o download como concluído.
        """

        fila = self.carregar()

        for item in fila:

            if item["video_id"] == video_id:

                item["caminho_download"] = caminho
                item["status"] = "pendente"

                self.salvar(fila)

                return True

        return False

    def obter_tentativas_download(self, video_id):
        """
        Retorna a quantidade de tentativas de download.
        """

        for item in self.carregar():

            if item["video_id"] == video_id:

                return item.get(
                    "tentativas_download",
                    0
                )

        return 0

    def proximo(self):
        """
        Retorna o primeiro vídeo pronto para publicação.

        Vídeos com download pendente não são publicados.
        """

        fila = self.carregar()

        for item in fila:

            if item.get("status") == "pendente":
                return item

        return None

    def remover(self, video_id):
        """
        Remove um vídeo da fila pelo ID.
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
        Retorna True quando não existem vídeos prontos
        para publicação.
        """

        return self.proximo() is None

    def possui_downloads_pendentes(self):
        """
        Retorna True quando existem downloads aguardando
        uma nova tentativa.
        """

        return bool(
            self.obter_downloads_pendentes()
        )