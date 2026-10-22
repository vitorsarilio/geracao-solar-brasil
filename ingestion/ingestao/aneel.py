"""Ingestão dos arquivos da ANEEL: descobre a URL, baixa o ZIP, extrai o CSV e grava Parquet."""

import io
import logging
import shutil
import zipfile
from pathlib import Path

import requests

from ingestao import ckan, rede
from ingestao.config import PACOTE_GD, RecursoAneel
from ingestao.parquet import csv_para_parquet

log = logging.getLogger(__name__)


SEPARADOR = '";"'


def normalizar_registros(linhas):
    """Gera um registro completo por vez a partir das linhas físicas do CSV da ANEEL.

    Todo registro tem o formato `"a";"b";...;"z"`. Alguns campos de texto livre trazem uma
    quebra de linha no meio, o que parte o registro em duas linhas físicas; aqui elas são
    juntadas (a quebra vira espaço). Devolve tuplas (registro, foi_reparado).
    """
    cabecalho = next(linhas).rstrip("\r\n")
    esperados = cabecalho.count(SEPARADOR)
    yield cabecalho, False

    buffer, partes = "", 0
    for linha in linhas:
        linha = linha.rstrip("\r\n")
        buffer = f"{buffer} {linha}" if partes else linha
        partes += 1
        encontrados = buffer.count(SEPARADOR)
        if encontrados == esperados and buffer.startswith('"') and buffer.endswith('"'):
            yield buffer, partes > 1
            buffer, partes = "", 0
        elif encontrados > esperados:
            raise RuntimeError(f"Registro com {encontrados + 1} colunas (esperado {esperados + 1}): {buffer[:200]!r}")

    if partes:
        raise RuntimeError(f"Arquivo terminou no meio de um registro: {buffer[:200]!r}")


def extrair_csv(caminho_zip: Path, destino: Path) -> tuple[Path, int]:
    """Extrai o único CSV do ZIP em streaming, já normalizado (1 registro por linha).

    O maior arquivo tem ~1,5 GB descompactado, então nada é carregado inteiro na memória.
    Devolve o caminho do CSV e quantos registros precisaram ser reparados.
    """
    with zipfile.ZipFile(caminho_zip) as zf:
        csvs = [m for m in zf.infolist() if m.filename.lower().endswith(".csv")]
        if len(csvs) != 1:
            raise RuntimeError(f"Esperava 1 CSV em {caminho_zip.name}, encontrei {len(csvs)}")
        membro = csvs[0]
        caminho_csv = destino / Path(membro.filename).name
        reparados = 0
        with zf.open(membro) as bruto, open(caminho_csv, "w", encoding="utf-8", newline="\n") as saida:
            linhas = io.TextIOWrapper(bruto, encoding="utf-8", newline="")
            for registro, reparado in normalizar_registros(linhas):
                saida.write(registro + "\n")
                reparados += reparado
    if reparados:
        log.warning("%s: %d registro(s) partido(s) em mais de uma linha foram reparados", membro.filename, reparados)
    return caminho_csv, reparados


def ingerir_recurso(sessao: requests.Session, cfg: RecursoAneel, dir_raw: Path) -> dict:
    """Processa um recurso de ponta a ponta e devolve a entrada do manifesto."""
    recurso = ckan.obter_recurso(sessao, PACOTE_GD, cfg.nome_recurso)
    temporario = dir_raw / "_tmp" / cfg.tabela
    temporario.mkdir(parents=True, exist_ok=True)
    try:
        caminho_zip = temporario / cfg.nome_recurso
        rede.baixar_arquivo(sessao, recurso.url, caminho_zip)
        caminho_csv, reparados = extrair_csv(caminho_zip, temporario)
        caminho_zip.unlink()  # libera disco antes da conversão

        caminho_parquet = dir_raw / f"{cfg.tabela}.parquet"
        log.info("Convertendo %s para Parquet", caminho_csv.name)
        linhas = csv_para_parquet(caminho_csv, caminho_parquet, cfg.colunas_removidas)
        log.info("%s: %s linhas", caminho_parquet.name, f"{linhas:,}".replace(",", "."))
    finally:
        shutil.rmtree(temporario, ignore_errors=True)

    return {
        "tabela": cfg.tabela,
        "fonte": "ANEEL",
        "recurso": recurso.nome,
        "url": recurso.url,
        "ultima_modificacao_fonte": recurso.ultima_modificacao,
        "linhas": linhas,
        "registros_reparados": reparados,
        "colunas_removidas": list(cfg.colunas_removidas),
    }
