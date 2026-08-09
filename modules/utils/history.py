from pathlib import Path

# Arquivo onde serão armazenados os IDs dos vídeos já baixados.
HISTORICO = Path("downloads/historico.txt")


def carregar_historico():
    """
    Retorna um conjunto (set) contendo todos os IDs já baixados.
    """

    if not HISTORICO.exists():
        return set()

    with open(HISTORICO, "r", encoding="utf-8") as arquivo:
        return {linha.strip() for linha in arquivo if linha.strip()}


def salvar_video(video_id):
    """
    Salva o ID de um vídeo no histórico.
    """

    HISTORICO.parent.mkdir(parents=True, exist_ok=True)

    with open(HISTORICO, "a", encoding="utf-8") as arquivo:
        arquivo.write(video_id + "\n")