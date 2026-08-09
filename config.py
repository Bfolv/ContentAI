# =====================================
# CONFIGURAÇÕES GERAIS DO PROJETO
# =====================================
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
    
# Chave da API do YouTube
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Nicho princial do canal
NICHO = "curiosidades"

# Quantidades de vídeos que serão buscados
QUANTIDADE_VIDEOS = 10

# Idioma utilizado na busca
IDIOMA = "pt"

# Duração mínima do Short (em segundos)
DURACAO_MINIMA = 20

# Duração máxima do Short (em segundos)
DURACAO_MAXIMA = 50

# Nota mínima para que um vídeo seja baixado.
MIN_SCORE_DOWNLOAD = 15