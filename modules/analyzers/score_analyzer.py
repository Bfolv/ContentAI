from modules.models.video import Video


class ScoreAnalyzer:
    """
    Responsável por calcular uma pontuação para um vídeo.

    Neste primeiro momento utilizaremos apenas regras simples.
    Conforme o projeto evoluir, novas regras serão adicionadas
    até que a pontuação seja baseada por IA.
    """

    def calcular(self, video: Video) -> float:

        score = 0

        # -----------------------------
        # Título
        # -----------------------------
        # Títulos maiores costumam ter mais contexto.
        if len(video.titulo) >= 40:
            score += 10

        # -----------------------------
        # Descrição
        # -----------------------------
        # Muitos canais deixam a descrição vazia.
        if len(video.descricao) >= 100:
            score += 5

        # -----------------------------
        # Thumbnail
        # -----------------------------
        # Se existe thumbnail, adicionamos alguns pontos.
        if video.thumbnail:
            score += 5

        video.score = score

        return score