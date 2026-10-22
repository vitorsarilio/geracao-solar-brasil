"""Fontes de dados e caminhos. Tudo que muda quando a fonte muda fica aqui."""

from dataclasses import dataclass
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
DIR_RAW = RAIZ_PROJETO / "data" / "raw"

# Portal de dados abertos da ANEEL (CKAN). A URL de download de cada recurso tem um
# ID que pode mudar, então ela é descoberta a cada execução pelo nome do recurso.
CKAN_PACKAGE_SHOW = "https://dadosabertos.aneel.gov.br/api/3/action/package_show"
PACOTE_GD = "relacao-de-empreendimentos-de-geracao-distribuida"

# Colunas com dados pessoais: nunca são gravadas, nem no dado bruto.
COLUNAS_PESSOAIS = ("NumCPFCNPJ", "NomTitularEmpreendimento", "CodCEP")


@dataclass(frozen=True)
class RecursoAneel:
    nome_recurso: str  # nome do recurso no portal (é por ele que achamos a URL)
    tabela: str  # nome do Parquet gerado em data/raw
    colunas_removidas: tuple[str, ...] = ()


RECURSOS_ANEEL = (
    RecursoAneel(
        nome_recurso="empreendimento-geracao-distribuida.zip",
        tabela="aneel_empreendimentos_gd",
        colunas_removidas=COLUNAS_PESSOAIS,
    ),
    # Arquivo técnico de fotovoltaica: é o único que traz a data de conexão (DatConexao)
    RecursoAneel(
        nome_recurso="empreendimento-gd-informacoes-tecnicas-fotovoltaica.zip",
        tabela="aneel_gd_fotovoltaica_tecnico",
    ),
)

# IBGE SIDRA, tabela 6579 (estimativa da população residente), variável 9324,
# todos os municípios (n6), último ano disponível.
SIDRA_POPULACAO = "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/last"
TABELA_POPULACAO = "ibge_populacao_municipios"

USER_AGENT = "geracao-solar-brasil (+https://github.com/vitorsarilio/geracao-solar-brasil)"
