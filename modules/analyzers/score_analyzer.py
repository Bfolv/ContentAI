import math


class ScoreAnalyzer:
    """
    Calcula o potencial de um vídeo em uma escala de 0 a 100.

    Distribuição:

        Visualizações  -> 40 pontos
        Engajamento    -> 35 pontos
        Retenção       -> 20 pontos
        Qualidade      -> 5 pontos

    A retenção ainda não está disponível para vídeos de terceiros.
    Os 20 pontos permanecem reservados para uma futura integração
    com dados reais de Analytics.
    """

    PESO_VIEWS = 40
    PESO_ENGAJAMENTO = 35
    PESO_RETENCAO = 20
    PESO_QUALIDADE = 5

    def calcular(self, video):
        """
        Calcula o score final do vídeo.

        Retorna:
            int: valor entre 0 e 100.
        """

        score_views = self._score_visualizacoes(
            video.views
        )

        score_engajamento = self._score_engajamento(
            video.views,
            video.likes,
            video.comentarios
        )

        score_retencao = self._score_retencao(
            video
        )

        score_qualidade = self._score_qualidade(
            video
        )

        score_final = (
            score_views
            + score_engajamento
            + score_retencao
            + score_qualidade
        )

        score_final = max(
            0,
            min(
                100,
                round(score_final)
            )
        )

        video.score = score_final

        return score_final

    # ==========================================================
    # VISUALIZAÇÕES
    # ==========================================================

    def _score_visualizacoes(self, views):
        """
        Até 40 pontos.

        Utilizamos escala logarítmica para representar alcance
        sem permitir que vídeos gigantes dominem completamente
        o score.
        """

        if views <= 0:
            return 0

        referencia = 1_000_000

        score = (
            math.log10(views + 1)
            / math.log10(referencia + 1)
        ) * self.PESO_VIEWS

        return min(
            self.PESO_VIEWS,
            score
        )

    # ==========================================================
    # ENGAJAMENTO
    # ==========================================================

    def _score_engajamento(
        self,
        views,
        likes,
        comentarios
    ):
        """
        Até 35 pontos.

        O engajamento é baseado principalmente na relação:

            likes / views

        Comentários funcionam como um indicador complementar.

        A intenção é valorizar vídeos que não apenas possuem
        muitas visualizações, mas conseguem gerar reação.
        """

        if views <= 0:
            return 0

        likes = max(0, likes)
        comentarios = max(0, comentarios)

        taxa_likes = likes / views
        taxa_comentarios = comentarios / views

        # ------------------------------------------------------
        # LIKES
        # ------------------------------------------------------
        #
        # Curva de referência:
        #
        # 1%  -> razoável
        # 2%  -> bom
        # 4%  -> muito bom
        # 6%+ -> excelente
        #
        # A curva é limitada para evitar que uma taxa absurda
        # ultrapasse o peso máximo.

        referencia_likes = 0.06

        score_likes = (
            taxa_likes
            / referencia_likes
        ) * 30

        score_likes = min(
            30,
            score_likes
        )

        # ------------------------------------------------------
        # COMENTÁRIOS
        # ------------------------------------------------------
        #
        # Comentários recebem menos peso porque são naturalmente
        # muito menos frequentes que likes.

        referencia_comentarios = 0.01

        score_comentarios = (
            taxa_comentarios
            / referencia_comentarios
        ) * 5

        score_comentarios = min(
            5,
            score_comentarios
        )

        return min(
            self.PESO_ENGAJAMENTO,
            score_likes + score_comentarios
        )

    # ==========================================================
    # RETENÇÃO
    # ==========================================================

    def _score_retencao(self, video):
        """
        Até 20 pontos.

        Atualmente não temos acesso à retenção média de vídeos
        de terceiros através da API utilizada pelo ContentAI.

        Portanto, não inventamos essa informação.

        Futuramente poderemos utilizar dados reais de Analytics
        para preencher esses 20 pontos.
        """

        return 0

    # ==========================================================
    # QUALIDADE
    # ==========================================================

    def _score_qualidade(self, video):
        """
        Até 5 pontos.

        Esta parte possui peso pequeno propositalmente.
        O desempenho real do vídeo é mais importante.
        """

        score = 0

        # Título minimamente desenvolvido.
        if video.titulo and len(video.titulo) >= 40:
            score += 2

        # Descrição minimamente desenvolvida.
        if video.descricao and len(video.descricao) >= 100:
            score += 1

        # Possui thumbnail.
        if video.thumbnail:
            score += 1

        # Duração válida.
        if video.duracao > 0:
            score += 1

        return min(
            self.PESO_QUALIDADE,
            score
        )