import io
import zipfile

import pytest

from ingestao.aneel import extrair_csv, normalizar_registros

CABECALHO = '"A";"B";"C"\n'


def _registros(texto):
    return list(normalizar_registros(io.StringIO(texto, newline="")))


def test_registros_normais_passam_intactos():
    assert _registros(CABECALHO + '"1";"2";"3"\r\n"4";"5";"6"\r\n') == [
        ('"A";"B";"C"', False),
        ('"1";"2";"3"', False),
        ('"4";"5";"6"', False),
    ]


def test_registro_partido_em_duas_linhas_e_juntado():
    # Caso real (arquivo técnico de fotovoltaica): quebra de linha dentro do modelo do módulo
    texto = CABECALHO + '"1";"SS-585-72MDH(T)\n";"EES5K"\n"4";"5";"6"\n'
    assert _registros(texto)[1:] == [('"1";"SS-585-72MDH(T) ";"EES5K"', True), ('"4";"5";"6"', False)]


def test_registro_com_colunas_a_mais_falha():
    with pytest.raises(RuntimeError, match="4 colunas"):
        _registros(CABECALHO + '"1";"2";"3";"4"\n')


def test_arquivo_terminando_no_meio_de_um_registro_falha():
    with pytest.raises(RuntimeError, match="meio de um registro"):
        _registros(CABECALHO + '"1";"2\n')


def test_extracao_conta_registros_reparados(tmp_path):
    caminho_zip = tmp_path / "x.zip"
    with zipfile.ZipFile(caminho_zip, "w") as zf:
        zf.writestr("dados.csv", (CABECALHO + '"1";"a\r\nb";"3"\r\n"4";"5";"6"\r\n').encode("utf-8"))

    csv, reparados = extrair_csv(caminho_zip, tmp_path)

    assert reparados == 1
    assert csv.read_text(encoding="utf-8") == '"A";"B";"C"\n"1";"a b";"3"\n"4";"5";"6"\n'
