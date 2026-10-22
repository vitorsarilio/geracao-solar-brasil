import pytest

from ingestao.ckan import RecursoNaoEncontrado, encontrar_recurso


def test_encontra_recurso_pelo_nome(resposta_ckan):
    recurso = encontrar_recurso(resposta_ckan, "empreendimento-geracao-distribuida.zip")
    assert recurso.url.endswith("/download/empreendimento-geracao-distribuida.zip")
    assert recurso.ultima_modificacao == "2026-10-10T05:55:29"


def test_recurso_ausente_lista_os_disponiveis(resposta_ckan):
    with pytest.raises(RecursoNaoEncontrado, match="Dicionário de dados"):
        encontrar_recurso(resposta_ckan, "arquivo-que-nao-existe.zip")


def test_resposta_sem_sucesso_falha():
    with pytest.raises(RuntimeError, match="sem sucesso"):
        encontrar_recurso({"success": False, "error": {"message": "Not found"}}, "qualquer.zip")
