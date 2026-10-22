-- Um registro por município, com a estimativa de população do ano mais recente.
-- O SIDRA devolve o nome em dois formatos ("Rio Branco - AC" e "São Paulo (SP)");
-- o nome limpo e a UF saem do mesmo texto.

with fonte as (
    select * from {{ source('ibge', 'ibge_populacao_municipios') }}
)

select
    {{ texto('cod_municipio') }}                                                as cod_municipio_ibge,
    trim(regexp_replace(nome_municipio, '\s*(-\s*[A-Z]{2}|\([A-Z]{2}\))\s*$', '')) as nome_municipio,
    regexp_extract(nome_municipio, '([A-Z]{2})\)?\s*$', 1)                     as sigla_uf,
    cast(ano as integer)                                                        as ano_referencia,
    cast(populacao as bigint)                                                   as populacao

from fonte
