-- Pergunta 2 (estados): onde está a geração, em valor absoluto e per capita.
-- "Watts por habitante" = kW instalados por 1.000 habitantes (as duas contas dão o mesmo número).

with sistemas as (
    select
        sigla_uf,
        count(*)                   as qtd_sistemas,
        sum(potencia_instalada_kw) as potencia_kw
    from {{ ref('int_gd_solar__empreendimentos') }}
    group by all
),

populacao as (
    select sigla_uf, sum(populacao) as populacao, max(ano_referencia) as ano_populacao
    from {{ ref('stg_ibge__populacao_municipios') }}
    group by all
),

base as (
    select
        u.sigla_uf,
        u.cod_uf_ibge,
        u.nome_uf,
        u.nome_regiao,
        coalesce(s.qtd_sistemas, 0) as qtd_sistemas,
        coalesce(s.potencia_kw, 0)  as potencia_kw,
        p.populacao,
        p.ano_populacao
    from {{ ref('ufs') }} as u
    left join sistemas as s using (sigla_uf)
    left join populacao as p using (sigla_uf)
)

select
    sigla_uf,
    cod_uf_ibge,
    nome_uf,
    nome_regiao,
    qtd_sistemas,
    cast(potencia_kw as double) as potencia_kw,
    potencia_kw / nullif(qtd_sistemas, 0)              as potencia_media_kw,
    populacao,
    ano_populacao,
    potencia_kw * 1000 / populacao                     as watts_por_habitante,
    qtd_sistemas * 1000.0 / populacao                  as sistemas_por_mil_habitantes,
    potencia_kw / sum(potencia_kw) over ()             as participacao_potencia,
    rank() over (order by potencia_kw desc)            as ranking_potencia,
    rank() over (order by potencia_kw / populacao desc) as ranking_per_capita
from base
order by ranking_potencia, sigla_uf
