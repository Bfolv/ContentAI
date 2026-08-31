# =====================================
# CONFIGURAÇÕES GERAIS DO PROJETO
# =====================================
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
    
# Chave da API do YouTube
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Chave da API da Anthropic (usada pelo RoteiroAgent
# para geração de roteiros autorais).
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Modelo utilizado pelo RoteiroAgent.
MODELO_ROTEIRO = "claude-sonnet-5"

# Limite de tokens de saída por formato de roteiro.
# Formatos curtos (Shorts/Reels) exigem roteiro enxuto.
# Formatos longos permitem desenvolvimento maior da narrativa.
LIMITE_TOKENS_ROTEIRO = {
    "curto": 1500,
    "longo": 4000,
}
# Nicho princial do canal
NICHO = "curiosidades"

# Quantidades de vídeos que serão buscados
QUANTIDADE_VIDEOS = 50

# Idioma utilizado na busca
IDIOMA = "pt"

# Duração mínima do Short (em segundos)
DURACAO_MINIMA = 20

# Duração máxima do Short (em segundos)
DURACAO_MAXIMA = 50

# Nota mínima para que um vídeo seja baixado.
MIN_SCORE_DOWNLOAD = 15