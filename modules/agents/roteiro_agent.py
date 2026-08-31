import json
from pathlib import Path

import anthropic

from config import ANTHROPIC_API_KEY
from config import LIMITE_TOKENS_ROTEIRO
from config import MODELO_ROTEIRO


# Arquivo padrão de personalidade do canal.
#
# No futuro, quando o dashboard multi-canal existir, cada
# perfil (ContentProfile) poderá apontar para o seu próprio
# arquivo de personalidade. Por enquanto, existe apenas um
# canal ativo, então usamos um único arquivo fixo.
ARQUIVO_PERSONALIDADE_PADRAO = Path("data/personalidade.json")


class RoteiroAgent:
    """
    Agente responsável por gerar roteiros originais via IA.

    Faz parte do pipeline "autoral" do ContentAI: em vez de
    buscar e baixar vídeo de terceiro (como o ShortsPipeline
    faz), esse agente GERA o conteúdo do zero, a partir da
    personalidade configurada do canal.

    Fluxo:

        personalidade.json
            ↓
        system prompt
            ↓
        Anthropic API
            ↓
        roteiro (texto puro, pronto para narração)

    O roteiro gerado ainda não passa por TTS nem edição de
    vídeo. Essas etapas serão responsabilidade de outros
    agentes, ainda não implementados, dentro do futuro
    AutoralPipeline.
    """

    def __init__(
        self,
        personalidade_path=None,
    ):

        self.client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY
        )

        caminho = (
            Path(personalidade_path)
            if personalidade_path
            else ARQUIVO_PERSONALIDADE_PADRAO
        )

        self.personalidade = self._carregar_personalidade(
            caminho
        )

    # ==========================================================
    # PERSONALIDADE
    # ==========================================================

    def _carregar_personalidade(self, caminho):
        """
        Carrega o perfil de personalidade do canal a partir
        de um arquivo JSON.

        Se o arquivo não existir, usa uma personalidade padrão
        mínima, apenas para não travar testes isolados do
        agente.

        Retorna:
            dict: dados de personalidade do canal.
        """

        if not caminho.exists():

            print(
                f"Aviso: arquivo de personalidade "
                f"'{caminho}' não encontrado."
            )

            print(
                "Usando personalidade padrão mínima."
            )

            return {
                "nome": "Canal Padrão",
                "nicho": "geral",
                "tom": "direto, ritmo rápido, humor seco",
                "regras": [],
                "formato_padrao": "curto",
            }

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    def _montar_system_prompt(self):
        """
        Monta o system prompt enviado à API a partir da
        personalidade carregada.

        Quanto mais específica a personalidade, menos
        genérico sai o roteiro. Por isso o prompt é
        propositalmente denso.
        """

        nome = self.personalidade.get(
            "nome",
            "Canal"
        )

        nicho = self.personalidade.get(
            "nicho",
            ""
        )

        tom = self.personalidade.get(
            "tom",
            ""
        )

        regras = self.personalidade.get(
            "regras",
            []
        )

        regras_texto = "\n".join(
            f"- {regra}" for regra in regras
        )

        return (
            f"Você é o roteirista do canal '{nome}'.\n\n"
            f"Nicho do canal: {nicho}\n"
            f"Tom de voz: {tom}\n\n"
            f"Regras obrigatórias de estilo:\n"
            f"{regras_texto}\n\n"
            "Escreva SOMENTE o roteiro final, em português, "
            "pronto para ser narrado em voz alta. Não inclua "
            "indicações de cena, marcações técnicas, títulos, "
            "markdown ou qualquer comentário fora do texto "
            "do roteiro."
        )

    # ==========================================================
    # GERAÇÃO
    # ==========================================================

    def gerar(
        self,
        tema,
        formato=None,
    ):
        """
        Gera um roteiro original sobre o tema informado.

        Args:
            tema (str):
                Assunto ou gancho do vídeo.

            formato (str | None):
                "curto" ou "longo". Define o limite de tokens
                da resposta. Se None, usa o formato_padrao
                definido na personalidade do canal.

        Retorna:
            str: roteiro gerado, pronto para narração.
        """

        formato = (
            formato
            or self.personalidade.get(
                "formato_padrao",
                "curto"
            )
        )

        if formato not in LIMITE_TOKENS_ROTEIRO:

            raise ValueError(
                f"Formato de roteiro inválido: '{formato}'. "
                f"Use um dos seguintes: "
                f"{list(LIMITE_TOKENS_ROTEIRO.keys())}"
            )

        max_tokens = LIMITE_TOKENS_ROTEIRO[formato]

        print(
            f"Gerando roteiro | formato={formato} | "
            f"max_tokens={max_tokens} | tema={tema}"
        )

        resposta = self.client.messages.create(

            model=MODELO_ROTEIRO,

            max_tokens=max_tokens,

            system=self._montar_system_prompt(),

            messages=[
                {
                    "role": "user",
                    "content": f"Tema do vídeo: {tema}",
                }
            ],
        )

        roteiro = resposta.content[0].text

        print(
            f"Roteiro gerado com sucesso "
            f"({len(roteiro)} caracteres)."
        )

        return roteiro


# ==================================================================
# TESTE ISOLADO
# ==================================================================
#
# Permite validar o RoteiroAgent sozinho, sem depender do
# AutoralPipeline (ainda não implementado) nem do restante
# do ContentAI.
#
# Executar de dentro da pasta ContentAI:
#
#     python -m modules.agents.roteiro_agent

if __name__ == "__main__":

    agente = RoteiroAgent()

    roteiro_gerado = agente.gerar(
        tema="uma história curta de terror urbano",
        formato="curto",
    )

    print("=" * 60)
    print("ROTEIRO GERADO:")
    print("=" * 60)
    print(roteiro_gerado)