from modules.models.content_profile import ContentProfile
from modules.utils.profiles import carregar_perfis, salvar_perfis


class ProfileManager:
    """
    Gerencia os perfis de conteúdo do ContentAI.

    Responsabilidades:
    - carregar perfis existentes;
    - adicionar novos perfis;
    - buscar perfis;
    - listar perfis;
    - salvar alterações automaticamente.
    """

    def __init__(self):

        # Carrega os perfis existentes do arquivo JSON.
        dados = carregar_perfis()

        self.perfis = []

        # Reconstrói os objetos ContentProfile.
        for dados_perfil in dados:

            perfil = ContentProfile(

                nome=dados_perfil["nome"],

                nicho=dados_perfil["nicho"],

                plataforma=dados_perfil["plataforma"],

                canal=dados_perfil["canal"],

                min_score_download=dados_perfil.get(
                    "min_score_download",
                    0
                ),

                # Novo campo da V1.2.
                #
                # Perfis antigos que ainda não possuem
                # esse campo serão automaticamente tratados
                # como Shorts.
                tipo_conteudo=dados_perfil.get(
                    "tipo_conteudo",
                    "shorts"
                ),
                 permitir_conteudo_reutilizado=dados_perfil.get(
                    "permitir_conteudo_reutilizado",
                    False
                )
            )

            self.perfis.append(
                perfil
            )

    def adicionar(self, perfil):
        """
        Adiciona um novo perfil e salva automaticamente.
        """

        # Evita cadastrar dois perfis com o mesmo nome.
        if self.buscar(perfil.nome) is not None:

            print(
                f"Perfil '{perfil.nome}' já existe."
            )

            return False

        self.perfis.append(
            perfil
        )

        # Persiste imediatamente a alteração.
        salvar_perfis(
            self.perfis
        )

        return True

    def buscar(self, nome):
        """
        Procura um perfil pelo nome.

        Retorna:
            ContentProfile | None
        """

        for perfil in self.perfis:

            if perfil.nome == nome:

                return perfil

        return None

    def listar(self):
        """
        Retorna uma cópia da lista de perfis.
        """

        return self.perfis.copy()