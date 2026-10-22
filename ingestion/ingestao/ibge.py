"""Ingestão da população municipal (IBGE SIDRA, tabela 6579)."""

import logging
from pathlib import Path

import requests

from ingestao.config import SIDRA_POPULACAO, TABELA_POPULACAO
from ingestao.rede import TIMEOUT
from ingestao.parquet import registros_para_parquet

log = logging.getLogger(__name__)

COLUNAS = ["cod_municipio", "nome_municipio", "ano", "populacao"]


def interpretar_sidra(dados: list[dict]) -> list[dict[str, str]]:
    """A API devolve a 1ª linha com os rótulos das colunas; o resto são os valores."""
    if not dados:
        raise RuntimeError("Resposta vazia do SIDRA")
    cabecalho = dados[0]
    if cabecalho.get("D1C") != "Município (Código)" or cabecalho.get("D3C") != "Ano (Código)":
        raise RuntimeError(f"Formato inesperado do SIDRA: {cabecalho}")

    return [
        {
            "cod_municipio": linha["D1C"],
            "nome_municipio": linha["D1N"],
            "ano": linha["D3C"],
            "populacao": linha["V"],
        }
        for linha in dados[1:]
    ]


def ingerir_populacao(sessao: requests.Session, dir_raw: Path) -> dict:
    log.info("Baixando população municipal do IBGE")
    resposta = sessao.get(SIDRA_POPULACAO, timeout=TIMEOUT)
    resposta.raise_for_status()
    registros = interpretar_sidra(resposta.json())

    caminho = dir_raw / f"{TABELA_POPULACAO}.parquet"
    linhas = registros_para_parquet(registros, COLUNAS, caminho)
    anos = sorted({r["ano"] for r in registros})
    log.info("%s: %s municípios, ano %s", caminho.name, linhas, ", ".join(anos))

    return {
        "tabela": TABELA_POPULACAO,
        "fonte": "IBGE SIDRA 6579",
        "url": SIDRA_POPULACAO,
        "ano_referencia": anos,
        "linhas": linhas,
    }
