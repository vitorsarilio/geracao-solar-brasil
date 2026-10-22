import shutil
import zipfile

import duckdb
import pytest

from ingestao import aneel, ckan, rede
from ingestao.config import COLUNAS_PESSOAIS, RecursoAneel
from ingestao.parquet import colunas_do_parquet, csv_para_parquet, garantir_sem_colunas


def _linhas(caminho):
    with duckdb.connect() as con:
        return con.execute(f"SELECT * FROM read_parquet('{caminho.as_posix()}') ORDER BY CodEmpreendimento").fetchall()


def test_extrai_o_csv_do_zip(zip_empreendimentos, tmp_path):
    destino = tmp_path / "saida"
    destino.mkdir()
    csv, _ = aneel.extrair_csv(zip_empreendimentos, destino)
    assert csv.name == "empreendimento-geracao-distribuida.csv"
    assert "Radiação solar" in csv.read_text(encoding="utf-8")


def test_zip_sem_exatamente_um_csv_falha(tmp_path):
    caminho = tmp_path / "vazio.zip"
    with zipfile.ZipFile(caminho, "w") as zf:
        zf.writestr("leia-me.txt", "nada")
    with pytest.raises(RuntimeError, match="Esperava 1 CSV"):
        aneel.extrair_csv(caminho, tmp_path)


def test_converte_csv_removendo_dados_pessoais(zip_empreendimentos, tmp_path):
    csv, _ = aneel.extrair_csv(zip_empreendimentos, tmp_path)
    saida = tmp_path / "empreendimentos.parquet"

    linhas = csv_para_parquet(csv, saida, COLUNAS_PESSOAIS)

    assert linhas == 3
    colunas = colunas_do_parquet(saida)
    assert not set(COLUNAS_PESSOAIS) & set(colunas)
    assert "CodEmpreendimento" in colunas and "MdaPotenciaInstaladaKW" in colunas


def test_dado_bruto_fica_como_texto_fiel_a_fonte(zip_empreendimentos, tmp_path):
    csv, _ = aneel.extrair_csv(zip_empreendimentos, tmp_path)
    saida = tmp_path / "empreendimentos.parquet"
    csv_para_parquet(csv, saida, COLUNAS_PESSOAIS)

    with duckdb.connect() as con:
        tipos = {nome: tipo for nome, tipo, *_ in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{saida.as_posix()}')").fetchall()}
    assert set(tipos.values()) == {"VARCHAR"}

    primeira = dict(zip(colunas_do_parquet(saida), _linhas(saida)[0]))
    assert primeira["MdaPotenciaInstaladaKW"] == "32,50"  # vírgula decimal preservada
    assert primeira["CodMunicipioIbge"] == "1200401"
    segunda = dict(zip(colunas_do_parquet(saida), _linhas(saida)[1]))
    assert segunda["NomMunicipio"] == "São Paulo"  # acentos preservados


def _registro(saida, codigo):
    with duckdb.connect() as con:
        cursor = con.execute(f"SELECT * FROM read_parquet('{saida.as_posix()}') WHERE CodEmpreendimento = ?", [codigo])
        return dict(zip([d[0] for d in cursor.description], cursor.fetchone()))


def test_aspas_soltas_dentro_do_campo_sao_preservadas(zip_empreendimentos, tmp_path):
    csv, _ = aneel.extrair_csv(zip_empreendimentos, tmp_path)
    saida = tmp_path / "completo.parquet"
    csv_para_parquet(csv, saida)  # sem remover colunas, para inspecionar o nome

    registro = _registro(saida, "GD.SP.000.009.999")
    assert registro["NomTitularEmpreendimento"] == 'EMERSON PAULA - ME - "JD. EUROPA"'
    assert registro["DatGeracaoConjuntoDados"] == "2026-10-10"  # aspa inicial removida


def test_campo_vazio_vira_nulo(zip_empreendimentos, tmp_path):
    csv, _ = aneel.extrair_csv(zip_empreendimentos, tmp_path)
    saida = tmp_path / "empreendimentos.parquet"
    csv_para_parquet(csv, saida, COLUNAS_PESSOAIS)
    assert _registro(saida, "GD.SP.000.009.999")["DscClasseConsumo"] is None


def test_linha_com_numero_errado_de_colunas_falha(tmp_path):
    csv = tmp_path / "quebrado.csv"
    csv.write_text('"A";"B";"C"\n"1";"2";"3"\n"4";"5"\n', encoding="utf-8")
    with pytest.raises(duckdb.Error):
        csv_para_parquet(csv, tmp_path / "quebrado.parquet")


def test_coluna_pessoal_ausente_na_fonte_nao_quebra(zip_empreendimentos, tmp_path):
    csv, _ = aneel.extrair_csv(zip_empreendimentos, tmp_path)
    assert csv_para_parquet(csv, tmp_path / "x.parquet", ("ColunaQueNaoExiste",)) == 3


def test_guarda_apaga_arquivo_com_coluna_proibida(zip_empreendimentos, tmp_path):
    csv, _ = aneel.extrair_csv(zip_empreendimentos, tmp_path)
    saida = tmp_path / "sem_remocao.parquet"
    csv_para_parquet(csv, saida)  # sem remover nada

    with pytest.raises(RuntimeError, match="NumCPFCNPJ"):
        garantir_sem_colunas(saida, COLUNAS_PESSOAIS)
    assert not saida.exists()


def test_ingere_recurso_de_ponta_a_ponta(zip_empreendimentos, tmp_path, monkeypatch, resposta_ckan):
    recurso = ckan.encontrar_recurso(resposta_ckan, "empreendimento-geracao-distribuida.zip")
    monkeypatch.setattr(ckan, "obter_recurso", lambda sessao, pacote, nome: recurso)
    monkeypatch.setattr(rede, "baixar_arquivo", lambda sessao, url, destino: shutil.copy(zip_empreendimentos, destino))

    cfg = RecursoAneel("empreendimento-geracao-distribuida.zip", "aneel_empreendimentos_gd", COLUNAS_PESSOAIS)
    dir_raw = tmp_path / "raw"
    entrada = aneel.ingerir_recurso(sessao=None, cfg=cfg, dir_raw=dir_raw)

    assert entrada["linhas"] == 3
    assert entrada["url"] == recurso.url
    assert (dir_raw / "aneel_empreendimentos_gd.parquet").exists()
    assert not (dir_raw / "_tmp").exists() or not any((dir_raw / "_tmp").iterdir())  # temporários apagados
