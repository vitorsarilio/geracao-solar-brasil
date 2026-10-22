"""Cliente HTTP com retentativas: os portais públicos às vezes oscilam."""

import logging
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ingestao.config import USER_AGENT

log = logging.getLogger(__name__)

TIMEOUT = (30, 120)  # (conexão, leitura) em segundos
TAMANHO_BLOCO = 1 << 20  # 1 MiB


def criar_sessao() -> requests.Session:
    sessao = requests.Session()
    retentativas = Retry(
        total=5,
        backoff_factor=2,  # 2, 4, 8, 16, 32 s
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    sessao.mount("https://", HTTPAdapter(max_retries=retentativas))
    sessao.headers["User-Agent"] = USER_AGENT
    return sessao


def baixar_arquivo(sessao: requests.Session, url: str, destino: Path) -> int:
    """Baixa em streaming para um arquivo temporário e só renomeia no fim (sem arquivo pela metade)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".part")
    log.info("Baixando %s", url)
    with sessao.get(url, stream=True, timeout=TIMEOUT) as resposta:
        resposta.raise_for_status()
        with open(parcial, "wb") as arquivo:
            for bloco in resposta.iter_content(TAMANHO_BLOCO):
                arquivo.write(bloco)
    parcial.replace(destino)
    tamanho = destino.stat().st_size
    log.info("Baixado: %s (%.1f MB)", destino.name, tamanho / 1e6)
    return tamanho
