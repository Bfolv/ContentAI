from datetime import datetime
from time import sleep

from main import main
from modules.services.scheduler import SchedulerService


# Intervalo entre as verificações do Scheduler.
INTERVALO_VERIFICACAO = 15

# Intervalo entre ciclos completos do ContentAI.
INTERVALO_CICLO = 0.15


def iniciar_ia():

    print("=" * 60)
    print("ContentAI - Modo Automático")
    print("IA ATIVADA")
    print("=" * 60)

    scheduler = SchedulerService(
        intervalo_minutos=INTERVALO_CICLO
    )

    while True:

        if scheduler.pode_executar():

            print()
            print("=" * 60)
            print(
                f"Ciclo iniciado: "
                f"{datetime.now()}"
            )
            print("=" * 60)

            scheduler.registrar_execucao()

            try:

                # Executa um ciclo completo.
                main()

            except Exception as erro:

                # Um erro em um ciclo não deve encerrar
                # o modo automático inteiro.
                print()
                print("Erro durante o ciclo:")
                print(f"Detalhes: {erro}")

            finally:

                # O intervalo começa a contar somente
                # depois que o ciclo terminou.
                scheduler.finalizar_execucao()

            print()
            print("Ciclo concluído.")

        else:

            restante = scheduler.tempo_restante()

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"Próximo ciclo em {restante}"
            )

        sleep(INTERVALO_VERIFICACAO)


if __name__ == "__main__":
    iniciar_ia()