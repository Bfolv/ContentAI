class Video:
    """
    Representa um vídeo encontrado pelo ContentAI.
    Durante o processamento, novas informações serão adicionadas
    ao objeto sem que seja necessário alterar outros módulos.
    """

    def __init__(
        self,
        video_id,
        titulo,
        descricao,
        canal,
        thumbnail,
        url,
        duracao,
        views,
        likes,
        comentarios,
        idioma,
        qualidade
    ):

        # ==========================
        # Dados vindos da API
        # ==========================

        self.video_id = video_id
        self.titulo = titulo
        self.descricao = descricao
        self.canal = canal
        self.thumbnail = thumbnail
        self.url = url

        self.duracao = duracao
        self.views = views
        self.likes = likes
        self.comentarios = comentarios
        self.idioma = idioma
        self.qualidade = qualidade

        # ==========================
        # Controle interno
        # ==========================

        self.score = 0
        self.status = "encontrado"
        self.caminho_download = None

    def __str__(self):

        return (
            f"\n"
            f"Título: {self.titulo}\n"
            f"Canal: {self.canal}\n"
            f"Views: {self.views}\n"
            f"Likes: {self.likes}\n"
            f"Comentários: {self.comentarios}\n"
            f"Duração: {self.duracao}\n"
            f"Idioma: {self.idioma}\n"
            f"Qualidade: {self.qualidade}\n"
            f"Status: {self.status}\n"
        )