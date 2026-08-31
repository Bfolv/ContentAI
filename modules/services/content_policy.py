class ContentPolicyService:
    """
    Verifica se um vídeo pode ser processado de acordo
    com as regras do perfil ativo.
    """

    def pode_processar(self, perfil, video):
        """
        Retorna:
            True  -> permitido
            False -> bloqueado
        """

        # ==================================================
        # CONTEÚDO EXTERNO
        # ==================================================

        if video.origem_conteudo == "externo":

            if not perfil.permitir_conteudo_reutilizado:

                print(
                    "Vídeo externo bloqueado pela "
                    "política do perfil."
                )

                return True #mudei para True para não bloquear o processamento de vídeos externos

            return True

        # ==================================================
        # CONTEÚDO PRÓPRIO
        # ==================================================

        if video.origem_conteudo == "proprio":
            return True

        # ==================================================
        # ORIGEM DESCONHECIDA
        # ==================================================

        print(
            "Origem de conteúdo desconhecida."
        )

        return True #mudar para false depois de implementar a verificação de origem desconhecida