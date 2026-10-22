-- Pergunta 2 (municípios): todos os municípios do IBGE, inclusive os que não têm GD solar
-- (aparecem com zero), em valor absoluto e per capita.

with sistemas as (
    select
        cod_municipio_ibge,
        count(*)                   as qtd_sistemas,
        sum(potencia_instalada_kw) as potencia_kw
    from {{ ref('int_gd_solar__empreendimentos') }}
    group by all
),

base as (
    select
        m.cod_municipio_ibge,
        m.nome_municipio,
        m.sigla_uf,
        u.nome_uf,
        u.nome_regiao,
        m.populacao,
        m.ano_referencia             as ano_populacao,
        coalesce(s.qtd_sistemas, 0)  as qtd_sistemas,
        coalesce(s.potencia_kw, 0)   as potencia_kw
    from {{ ref('stg_ibge__populacao_municipios') }} as m
    left join sistemas as s using (cod_municipio_ibge)
    left join {{ ref('ufs') }} as u using (sigla_uf)
)

select
    cod_municipio_ibge,
    nome_municipio,
    sigla_uf,
    nome_uf,
    nome_regiao,
    populacao,
    ano_populacao,
    qtd_sistemas,
    cast(potencia_kw as double) as potencia_kw,
    potencia_kw / nullif(qtd_sistemas, 0)                              as potencia_media_kw,
    potencia_kw * 1000 / populacao                                     as watts_por_habitante,
    qtd_sistemas * 1000.0 / populacao                                  as sistemas_por_mil_habitantes,
    rank() over (order by potencia_kw desc)                            as ranking_potencia_brasil,
    rank() over (order by potencia_kw / populacao desc)                as ranking_per_capita_brasil,
    rank() over (partition by sigla_uf order by potencia_kw desc)      as ranking_potencia_uf
from base
order by ranking_potencia_brasil, cod_municipio_ibge
