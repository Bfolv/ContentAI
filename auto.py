from time import sleep
from datetime import datetime

from main import main
from modules.services.scheduler import SchedulerService


# Intervalo usado apenas para verificar se chegou
# o momento de executar um novo ciclo.
INTERVALO_VERIFICACAO = 30


def iniciar_ia():

    print("=" * 60)
    print("ContentAI - Modo Automático")
    print("IA ATIVADA")
    print("=" * 60)

    # O Scheduler é criado apenas uma vez.
    scheduler = SchedulerService(
        intervalo_minutos=1
    )

    while True:

        # Verifica se chegou o momento do próximo ciclo.
        if scheduler.pode_executar():

            print()
            print("=" * 60)
            print(
                f"Ciclo iniciado: "
                f"{datetime.now()}"
            )
            print("=" * 60)

            # Registra o início do ciclo.
            scheduler.registrar_execucao()

            try:

                # Executa UM ciclo completo do ContentAI.
                main()

            finally:

                # Registra o momento em que o ciclo terminou.
                scheduler.finalizar_execucao()

            print()
            print("Ciclo concluído.")

        else:

            restante = scheduler.tempo_restante()

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"Próximo ciclo em {restante}"
            )

        # Aguarda antes de verificar novamente.
        sleep(INTERVALO_VERIFICACAO)


if __name__ == "__main__":
    iniciar_ia()