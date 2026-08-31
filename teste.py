from modules.agents.roteiro_agent import RoteiroAgent


# ==================================================================
# TESTE ISOLADO DO ROTEIRO AGENT
# ==================================================================
#
# Objetivo: validar que o agente carrega a personalidade
# corretamente e consegue gerar um roteiro através da API
# da Anthropic, sem depender do AutoralPipeline (ainda não
# implementado).

agente = RoteiroAgent()

print()
print("Personalidade carregada:")
print(agente.personalidade)

roteiro = agente.gerar(
    tema="uma história curta de terror urbano",
    formato="curto",
)

print()
print("=" * 60)
print("ROTEIRO GERADO:")
print("=" * 60)
print(roteiro)