import duckdb
import pytest

from ingestao.ibge import COLUNAS, interpretar_sidra
from ingestao.parquet import registros_para_parquet


def test_interpreta_resposta_do_sidra(resposta_sidra):
    registros = interpretar_sidra(resposta_sidra)
    assert registros == [
        {"cod_municipio": "1200401", "nome_municipio": "Rio Branco - AC", "ano": "2026", "populacao": "391243"},
        {"cod_municipio": "3550308", "nome_municipio": "São Paulo (SP)", "ano": "2026", "populacao": "11911337"},
    ]


def test_formato_inesperado_falha():
    with pytest.raises(RuntimeError, match="Formato inesperado"):
        interpretar_sidra([{"D1C": "Estado (Código)", "D3C": "Ano (Código)"}])


def test_resposta_vazia_falha():
    with pytest.raises(RuntimeError, match="vazia"):
        interpretar_sidra([])


def test_grava_populacao_em_parquet(resposta_sidra, tmp_path):
    caminho = tmp_path / "pop.parquet"
    assert registros_para_parquet(interpretar_sidra(resposta_sidra), COLUNAS, caminho) == 2
    with duckdb.connect() as con:
        total = con.execute(f"SELECT sum(populacao::BIGINT) FROM read_parquet('{caminho.as_posix()}')").fetchone()[0]
    assert total == 391243 + 11911337
