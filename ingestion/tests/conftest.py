import zipfile
from pathlib import Path

import pytest

# Mesmo formato do arquivo real da ANEEL: ";" como separador, tudo entre aspas,
# decimal com vírgula, UTF-8 com acentos, CPF mascarado e CEP com espaços.
CSV_EMPREENDIMENTOS = (
    '"DatGeracaoConjuntoDados";"SigUF";"CodMunicipioIbge";"NomMunicipio";"DscClasseConsumo";'
    '"CodCEP";"NumCPFCNPJ";"CodEmpreendimento";"SigTipoGeracao";"DscFonteGeracao";'
    '"MdaPotenciaInstaladaKW";"NomTitularEmpreendimento"\n'
    '"2026-10-10";"AC";"1200401";"Rio Branco";"Comercial";"69912452  ";"12005360000165";'
    '"GD.AC.000.000.590";"UFV";"Radiação solar";"32,50";"ELITE ENGENHARIA LTDA"\n'
    '"2026-10-10";"SP";"3550308";"São Paulo";"Residencial";"01310***";"***.754.418-**";'
    '"GD.SP.000.001.552";"UFV";"Radiação solar";"2,00";"FULANO DE TAL"\n'
    # Caso real: aspas soltas dentro de um campo e campo vazio
    '"2026-10-10";"SP";"3550308";"São Paulo";"";"01310***";"***.111.222-**";'
    '"GD.SP.000.009.999";"UFV";"Radiação solar";"5,00";"EMERSON PAULA - ME - "JD. EUROPA""\n'
)


@pytest.fixture
def zip_empreendimentos(tmp_path: Path) -> Path:
    caminho = tmp_path / "empreendimento-geracao-distribuida.zip"
    with zipfile.ZipFile(caminho, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("empreendimento-geracao-distribuida.csv", CSV_EMPREENDIMENTOS.encode("utf-8"))
    return caminho


@pytest.fixture
def resposta_ckan() -> dict:
    base = "https://dadosabertos.aneel.gov.br/dataset/x/resource"
    return {
        "success": True,
        "result": {
            "resources": [
                {"name": "Dicionário de dados", "url": f"{base}/1/download/dm.pdf", "last_modified": "2026-06-12T17:09:51"},
                {
                    "name": "empreendimento-geracao-distribuida.zip",
                    "url": f"{base}/2/download/empreendimento-geracao-distribuida.zip",
                    "last_modified": "2026-10-10T05:55:29",
                },
            ]
        },
    }


@pytest.fixture
def resposta_sidra() -> list[dict]:
    return [
        {"D1C": "Município (Código)", "D1N": "Município", "D3C": "Ano (Código)", "V": "Valor"},
        {"D1C": "1200401", "D1N": "Rio Branco - AC", "D3C": "2026", "V": "391243"},
        {"D1C": "3550308", "D1N": "São Paulo (SP)", "D3C": "2026", "V": "11911337"},
    ]
