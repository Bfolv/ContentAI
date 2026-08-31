from modules.services.profile_manager import ProfileManager


class ActiveProfileService:
    """
    Responsável por fornecer o perfil ativo do ContentAI.

    Por enquanto o sistema trabalha com apenas um perfil.
    Futuramente poderá existir seleção de perfil, múltiplos
    nichos e múltiplas contas.
    """

    PERFIL_ATIVO = "Rick and Morty"

    def __init__(self):

        self.profile_manager = ProfileManager()

    def obter(self):
        """
        Retorna o perfil atualmente utilizado pelo ContentAI.

        Retorna:
            ContentProfile | None
        """

        perfil = self.profile_manager.buscar(
            self.PERFIL_ATIVO
        )

        if perfil is None:

            print(
                f"Erro: perfil ativo "
                f"'{self.PERFIL_ATIVO}' não encontrado."
            )

            return None

        return perfil

    def obter_tipo_conteudo(self):
        """
        Retorna o tipo de conteúdo definido no perfil ativo.

        Exemplos:
            shorts
            longos
            autoral

        Se o perfil não existir, retorna None.
        """

        perfil = self.obter()

        if perfil is None:

            return None

        return perfil.tipo_conteudo