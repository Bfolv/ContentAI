from datetime import datetime, timedelta
from pathlib import Path
import json


class SchedulerService:
    """
    Responsável por controlar o intervalo entre as execuções
    do ContentAI.

    O estado da última execução é salvo em disco para que
    o Scheduler não perca a informação quando o programa
    for fechado.
    """

    def __init__(self, intervalo_minutos=60):

        # Intervalo mínimo entre duas execuções.
        self.intervalo = timedelta(minutes=intervalo_minutos)

        # Arquivo responsável por armazenar o estado.
        self.arquivo_estado = Path("data/scheduler.json")

        # Garante que a pasta exista.
        self.arquivo_estado.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Recupera a última execução salva.
        self.ultima_execucao = self._carregar_estado()

    def _carregar_estado(self):
        """
        Carrega a última execução do arquivo de estado.

        Returns:
            datetime | None:
                Data da última execução ou None caso
                ainda não exista um estado salvo.
        """

        if not self.arquivo_estado.exists():
            return None

        try:

            with open(
                self.arquivo_estado,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(arquivo)

            ultima_execucao = dados.get("ultima_execucao")

            if not ultima_execucao:
                return None

            return datetime.fromisoformat(ultima_execucao)

        except (json.JSONDecodeError, ValueError, TypeError):

            # Se o arquivo estiver inválido, começamos novamente.
            return None

    def _salvar_estado(self):
        """
        Salva o estado atual do Scheduler.
        """

        dados = {
            "ultima_execucao": (
                self.ultima_execucao.isoformat()
                if self.ultima_execucao
                else None
            )
        }

        with open(
            self.arquivo_estado,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados,
                arquivo,
                indent=4
            )

    def pode_executar(self):
        """
        Verifica se já passou tempo suficiente desde
        a última execução.

        Returns:
            bool:
                True se pode executar.
                False caso ainda precise aguardar.
        """

        # Nunca executou anteriormente.
        if self.ultima_execucao is None:
            return True

        agora = datetime.now()

        tempo_passado = agora - self.ultima_execucao

        return tempo_passado >= self.intervalo

    def registrar_execucao(self):
        """
        Registra o início de uma execução.
        O horário é mantido apenas durante o ciclo atual.
        O intervalo entre ciclos será contado a partir
        da finalização.
        """

        self.ultima_execucao = datetime.now()

    def finalizar_execucao(self):
        """
        Registra o momento em que o ciclo terminou.

        A partir deste momento começa a contagem
        do intervalo até o próximo ciclo.
        """

        self.ultima_execucao = datetime.now()

        self._salvar_estado()

    def proxima_execucao(self):
        """
        Retorna o horário previsto para a próxima execução.
        """

        if self.ultima_execucao is None:
            return datetime.now()

        return self.ultima_execucao + self.intervalo

    def tempo_restante(self):
        """
        Retorna quanto tempo falta para a próxima execução.

        Returns:
            timedelta:
                Tempo restante.
        """

        if self.ultima_execucao is None:
            return timedelta(0)

        restante = self.proxima_execucao() - datetime.now()

        if restante.total_seconds() < 0:
            return timedelta(0)

        return restante