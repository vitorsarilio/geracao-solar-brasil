"""Uso: python -m ingestao [--fontes aneel ibge] [--dir-raw data/raw]"""

import argparse
import json
import logging
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from ingestao import aneel, ibge
from ingestao.config import DIR_RAW, RECURSOS_ANEEL
from ingestao.rede import criar_sessao

log = logging.getLogger("ingestao")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Baixa os dados da ANEEL e do IBGE para data/raw em Parquet.")
    parser.add_argument("--fontes", nargs="+", choices=["aneel", "ibge"], default=["aneel", "ibge"])
    parser.add_argument("--dir-raw", type=Path, default=DIR_RAW)
    args = parser.parse_args(argv)

    # Acentos corretos no log também em terminais do Windows que não usam UTF-8 por padrão
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    inicio = time.monotonic()
    args.dir_raw.mkdir(parents=True, exist_ok=True)
    sessao = criar_sessao()

    tabelas = []
    if "ibge" in args.fontes:
        tabelas.append(ibge.ingerir_populacao(sessao, args.dir_raw))
    if "aneel" in args.fontes:
        for cfg in RECURSOS_ANEEL:
            tabelas.append(aneel.ingerir_recurso(sessao, cfg, args.dir_raw))

    shutil.rmtree(args.dir_raw / "_tmp", ignore_errors=True)

    manifesto = {
        "executado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duracao_s": round(time.monotonic() - inicio, 1),
        "tabelas": tabelas,
    }
    (args.dir_raw / "_manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Ingestão concluída em %.0f s", manifesto["duracao_s"])


if __name__ == "__main__":
    main()
