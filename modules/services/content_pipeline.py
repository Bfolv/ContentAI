from modules.services.pipelines.shorts_pipeline import ShortsPipeline


class ContentPipelineService:
    """
    Gerenciador central dos pipelines do ContentAI.

    O main.py não conhece os pipelines diretamente.
    Ele apenas informa o tipo de conteúdo e deixa este
    serviço decidir qual pipeline deve executar.
    """

    def __init__(
        self,
        analyzer,
        downloader,
        fila,
        uploader,
        historico,
    ):
        self.pipelines = {
            "shorts": ShortsPipeline(
                analyzer=analyzer,
                downloader=downloader,
                fila=fila,
                uploader=uploader,
                historico=historico,
            ),
            "longos": None,
            "autoral": None,
            "musica": None,
        }

    # ==========================================================
    # CONSULTA
    # ==========================================================

    def obter_pipeline(self, tipo_conteudo):
        return self.pipelines.get(tipo_conteudo)

    def possui(self, tipo_conteudo):
        return tipo_conteudo in self.pipelines

    def disponiveis(self):
        return list(self.pipelines.keys())

    # ==========================================================
    # FILA
    # ==========================================================

    def processar_fila(self, tipo_conteudo):
        """
        Entrega a fila pendente ao pipeline responsável.

        A fila pertence ao fluxo de publicação, portanto o main.py
        não deve conhecer detalhes de upload ou recuperação.
        """

        pipeline = self.obter_pipeline(tipo_conteudo)

        if pipeline is None:
            print(
                f"\nPipeline '{tipo_conteudo}' "
                "ainda não implementado."
            )
            return False

        return pipeline.processar_fila()

    # ==========================================================
    # EXECUÇÃO
    # ==========================================================

    def executar(
        self,
        tipo_conteudo,
        videos,
        perfil,
    ):
        """
        Executa o pipeline correspondente ao tipo de conteúdo.

        Retorna:
            True  -> processamento concluído.
            False -> pipeline inexistente ou falha.
        """

        pipeline = self.obter_pipeline(tipo_conteudo)

        if pipeline is None:
            print(
                f"\nPipeline '{tipo_conteudo}' "
                "ainda não implementado."
            )
            return False

        return pipeline.processar(
            videos=videos,
            perfil=perfil,
        )