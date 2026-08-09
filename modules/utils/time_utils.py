import re


def converter_duracao_para_segundos(duracao: str) -> int:
    """
    Converte a duração ISO 8601 do YouTube para segundos.

    Exemplos:
        PT14S -> 14
        PT1M20S -> 80
        PT2M -> 120
        PT1H2M15S -> 3735
    """

    horas = minutos = segundos = 0

    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        duracao
    )

    if match:

        horas = int(match.group(1) or 0)
        minutos = int(match.group(2) or 0)
        segundos = int(match.group(3) or 0)

    return horas * 3600 + minutos * 60 + segundos