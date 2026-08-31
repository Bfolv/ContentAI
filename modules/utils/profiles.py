import json
from pathlib import Path


ARQUIVO_PERFIS = Path("data/profiles.json")


def carregar_perfis():
    """
    Carrega os perfis salvos no arquivo JSON.

    Retorna:
        list:
            Lista de dicionários contendo os perfis.
    """

    if not ARQUIVO_PERFIS.exists():
        return []

    with open(
        ARQUIVO_PERFIS,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)


def salvar_perfis(perfis):
    """
    Salva os objetos ContentProfile no arquivo JSON.
    """

    # Garante que a pasta exista.
    ARQUIVO_PERFIS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dados = []

    for perfil in perfis:

        dados.append(
            {
                "nome": perfil.nome,

                "nicho": perfil.nicho,

                "plataforma": perfil.plataforma,

                "canal": perfil.canal,

                "min_score_download":
                    perfil.min_score_download,

                "tipo_conteudo":
                    perfil.tipo_conteudo,

                "permitir_conteudo_reutilizado":
                    perfil.permitir_conteudo_reutilizado
            }
        )

    with open(
        ARQUIVO_PERFIS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )