"""Descobre a URL atual de um recurso no portal CKAN da ANEEL."""

from dataclasses import dataclass

import requests

from ingestao.config import CKAN_PACKAGE_SHOW
from ingestao.rede import TIMEOUT


class RecursoNaoEncontrado(LookupError):
    pass


@dataclass(frozen=True)
class Recurso:
    nome: str
    url: str
    ultima_modificacao: str | None


def encontrar_recurso(resposta: dict, nome: str) -> Recurso:
    """Acha o recurso pelo nome na resposta do `package_show`."""
    if not resposta.get("success"):
        raise RuntimeError(f"O portal respondeu sem sucesso: {resposta.get('error')}")

    recursos = resposta["result"]["resources"]
    for recurso in recursos:
        if recurso.get("name") == nome:
            return Recurso(
                nome=recurso["name"],
                url=recurso["url"],
                ultima_modificacao=recurso.get("last_modified"),
            )

    disponiveis = ", ".join(sorted(r.get("name", "?") for r in recursos))
    raise RecursoNaoEncontrado(f"Recurso '{nome}' não encontrado. Disponíveis: {disponiveis}")


def obter_recurso(sessao: requests.Session, pacote: str, nome: str) -> Recurso:
    resposta = sessao.get(CKAN_PACKAGE_SHOW, params={"id": pacote}, timeout=TIMEOUT)
    resposta.raise_for_status()
    return encontrar_recurso(resposta.json(), nome)
