"""Conversão para Parquet com DuckDB (lê em streaming, sem carregar o CSV inteiro na memória)."""

from pathlib import Path

import duckdb


def _sql_texto(caminho: Path) -> str:
    """Caminho como literal SQL (barras normais funcionam no Windows e no Linux)."""
    return "'" + caminho.as_posix().replace("'", "''") + "'"


def _sql_coluna(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def colunas_do_parquet(caminho: Path) -> list[str]:
    with duckdb.connect() as con:
        return [linha[0] for linha in con.execute(f"DESCRIBE SELECT * FROM read_parquet({_sql_texto(caminho)})").fetchall()]


def contar_linhas(caminho: Path) -> int:
    with duckdb.connect() as con:
        return con.execute(f"SELECT count(*) FROM read_parquet({_sql_texto(caminho)})").fetchone()[0]


def csv_para_parquet(caminho_csv: Path, caminho_parquet: Path, colunas_removidas: tuple[str, ...] = ()) -> int:
    """Converte o CSV da ANEEL para Parquet, tudo como texto.

    O arquivo tem todo campo entre aspas e separado por ";", mas alguns campos de texto
    livre trazem aspas soltas (ex.: `MERCEARIA - "JD. EUROPA"`), que quebram um leitor
    de CSV comum. Como toda linha tem o formato `"a";"b";...;"z"`, lemos com `";"` como
    separador e sem tratar aspas, e tiramos só a aspa inicial da 1ª coluna e a final da
    última. O modo estrito do DuckDB continua falhando se uma linha vier com outro número
    de colunas.

    A conversão de tipos (decimal com vírgula, datas, códigos) fica no staging do dbt,
    para o dado bruto continuar fiel à fonte. Retorna o número de linhas gravadas.
    """
    caminho_parquet.parent.mkdir(parents=True, exist_ok=True)
    leitura = (
        f"read_csv({_sql_texto(caminho_csv)}, delim='\";\"', quote='', escape='', header=true, "
        "all_varchar=true, encoding='utf-8', strict_mode=true)"
    )
    with duckdb.connect() as con:
        brutas = [linha[0] for linha in con.execute(f"DESCRIBE SELECT * FROM {leitura}").fetchall()]
        limpas = [nome.strip('"') for nome in brutas]

        expressoes = []
        for i, (bruta, limpa) in enumerate(zip(brutas, limpas)):
            if limpa in colunas_removidas:
                continue
            valor = _sql_coluna(bruta)
            # Remove exatamente uma aspa da ponta da linha (valores com aspas internas ficam intactos)
            if i == 0:
                valor = f"regexp_replace({valor}, '^\"', '')"
            if i == len(brutas) - 1:
                valor = f"regexp_replace({valor}, '\"$', '')"
            expressoes.append(f"{valor} AS {_sql_coluna(limpa)}")

        con.execute(
            f"COPY (SELECT {', '.join(expressoes)} FROM {leitura}) "
            f"TO {_sql_texto(caminho_parquet)} (FORMAT parquet, COMPRESSION zstd)"
        )

    garantir_sem_colunas(caminho_parquet, colunas_removidas)
    return contar_linhas(caminho_parquet)


def registros_para_parquet(registros: list[dict[str, str]], colunas: list[str], caminho_parquet: Path) -> int:
    """Grava uma lista pequena de registros (ex.: resposta de API) como Parquet de texto."""
    caminho_parquet.parent.mkdir(parents=True, exist_ok=True)
    definicao = ", ".join(f"{_sql_coluna(c)} VARCHAR" for c in colunas)
    with duckdb.connect() as con:
        con.execute(f"CREATE TABLE registros ({definicao})")
        con.executemany(
            f"INSERT INTO registros VALUES ({', '.join('?' for _ in colunas)})",
            [[r.get(c) for c in colunas] for r in registros],
        )
        con.execute(f"COPY registros TO {_sql_texto(caminho_parquet)} (FORMAT parquet, COMPRESSION zstd)")
    return len(registros)


def garantir_sem_colunas(caminho_parquet: Path, colunas: tuple[str, ...]) -> None:
    """Falha se alguma coluna proibida (ex.: dado pessoal) estiver no arquivo gerado."""
    presentes = set(colunas) & set(colunas_do_parquet(caminho_parquet))
    if presentes:
        caminho_parquet.unlink(missing_ok=True)
        raise RuntimeError(f"Colunas proibidas no Parquet gerado: {sorted(presentes)}")
