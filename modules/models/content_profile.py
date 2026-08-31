class ContentProfile:

    def __init__(
        self,
        nome,
        nicho,
        plataforma,
        canal,
        min_score_download=0,
        tipo_conteudo="shorts",
        permitir_conteudo_reutilizado=True
    ):

        self.nome = nome
        self.nicho = nicho
        self.plataforma = plataforma
        self.canal = canal
        self.min_score_download = min_score_download
        self.tipo_conteudo = tipo_conteudo
        self.permitir_conteudo_reutilizado = (
            permitir_conteudo_reutilizado
        )