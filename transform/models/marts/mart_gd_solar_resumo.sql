-- Uma linha com os números de destaque e as datas de referência (cabeçalho do dashboard).

with sistemas as (
    select * from {{ ref('int_gd_solar__empreendimentos') }}
),

populacao as (
    select sum(populacao) as populacao, max(ano_referencia) as ano_populacao
    from {{ ref('stg_ibge__populacao_municipios') }}
),

totais as (
    select
        count(*)                                           as qtd_sistemas,
        sum(potencia_instalada_kw)                         as potencia_kw,
        count(distinct cod_municipio_ibge)                 as qtd_municipios_com_gd_solar,
        count(*) filter (where data_conexao is null)       as qtd_sistemas_sem_data_conexao
    from sistemas
)

select
    p.data_publicacao_dados,
    p.ultima_data_conexao,
    p.ultimo_mes_fechado,
    p.mes_referencia,
    p.qtd_meses_provisorios,
    t.qtd_sistemas,
    cast(t.potencia_kw as double) as potencia_kw,
    t.potencia_kw / t.qtd_sistemas            as potencia_media_kw,
    t.qtd_municipios_com_gd_solar,
    t.qtd_sistemas_sem_data_conexao,
    pop.populacao,
    pop.ano_populacao,
    t.potencia_kw * 1000 / pop.populacao      as watts_por_habitante
from totais as t
cross join {{ ref('int_gd_solar__periodo_referencia') }} as p
cross join populacao as pop
