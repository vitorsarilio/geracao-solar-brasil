-- Pergunta 3: divisão por classe de consumo, ano a ano.
-- Grão: ano de conexão × classe de consumo. Vai até o último mês fechado; o ano corrente
-- (ou um ano com meses provisórios) vem com ano_completo = false.

with periodo as (
    select * from {{ ref('int_gd_solar__periodo_referencia') }}
),

sistemas as (
    select s.*
    from {{ ref('int_gd_solar__empreendimentos') }} as s
    cross join periodo as p
    where s.mes_conexao <= p.ultimo_mes_fechado
),

anual as (
    select
        ano_conexao                as ano,
        grupo_classe_consumo,
        classe_consumo,
        count(*)                   as qtd_conexoes,
        sum(potencia_instalada_kw) as potencia_adicionada_kw
    from sistemas
    group by all
)

select
    anual.ano,
    anual.grupo_classe_consumo,
    anual.classe_consumo,
    anual.qtd_conexoes,
    cast(anual.potencia_adicionada_kw as double) as potencia_adicionada_kw,
    anual.potencia_adicionada_kw / sum(anual.potencia_adicionada_kw) over (partition by anual.ano) as participacao_potencia_no_ano,
    anual.ano < year(periodo.mes_referencia)
        or (anual.ano = year(periodo.mes_referencia) and month(periodo.mes_referencia) = 12)    as ano_completo
from anual
cross join periodo
order by anual.ano, anual.potencia_adicionada_kw desc, anual.classe_consumo
