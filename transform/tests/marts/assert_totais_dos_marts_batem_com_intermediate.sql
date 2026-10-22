-- Reconciliação: a potência total de cada mart tem que bater com a camada intermediária
-- (nenhum sistema some nem é contado duas vezes nas agregações). Tolerância de 1 kW
-- para arredondamento de ponto flutuante. Retorna as linhas que não batem.

with base as (
    select
        sum(potencia_instalada_kw) as total,
        sum(potencia_instalada_kw) filter (
            where mes_conexao <= (select ultimo_mes_fechado from {{ ref('int_gd_solar__periodo_referencia') }})
        ) as total_com_data_ate_ultimo_mes_fechado
    from {{ ref('int_gd_solar__empreendimentos') }}
),

marts as (
    select 'mart_gd_solar_uf' as mart, sum(potencia_kw) as total, 'total' as comparar_com
    from {{ ref('mart_gd_solar_uf') }}
    union all
    select 'mart_gd_solar_municipio', sum(potencia_kw), 'total'
    from {{ ref('mart_gd_solar_municipio') }}
    union all
    select 'mart_gd_solar_resumo', sum(potencia_kw), 'total'
    from {{ ref('mart_gd_solar_resumo') }}
    union all
    select 'fct_gd_solar_mensal', sum(potencia_adicionada_kw), 'com_data'
    from {{ ref('fct_gd_solar_mensal') }}
    union all
    select 'mart_gd_solar_classe_anual', sum(potencia_adicionada_kw), 'com_data'
    from {{ ref('mart_gd_solar_classe_anual') }}
)

select
    m.mart,
    m.total as total_mart,
    case m.comparar_com when 'total' then b.total else b.total_com_data_ate_ultimo_mes_fechado end as total_esperado
from marts as m
cross join base as b
where abs(m.total - case m.comparar_com when 'total' then b.total else b.total_com_data_ate_ultimo_mes_fechado end) > 1
