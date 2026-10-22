-- Pergunta 1: como a potência instalada cresceu ao longo do tempo?
-- Grão: mês × UF × grupo de classe de consumo, com a grade completa (meses sem conexão
-- aparecem com zero). Assim o acumulado fica correto em qualquer agregação.
-- Vai até o último mês fechado; os meses depois do mês de referência vêm com
-- mes_provisorio = true (ainda incompletos por atraso de cadastro).

with sistemas as (
    select * from {{ ref('int_gd_solar__empreendimentos') }}
    where data_conexao is not null
),

periodo as (
    select * from {{ ref('int_gd_solar__periodo_referencia') }}
),

meses as (
    select cast(mes as date) as mes
    from range(
        (select min(mes_conexao) from sistemas),
        (select ultimo_mes_fechado from periodo) + interval 1 month,
        interval 1 month
    ) as t(mes)
),

grade as (
    select m.mes, u.sigla_uf, u.nome_uf, u.nome_regiao, g.grupo_classe_consumo
    from meses as m
    cross join {{ ref('ufs') }} as u
    cross join (select distinct grupo_classe_consumo from {{ ref('classes_consumo') }}) as g
),

mensal as (
    select
        mes_conexao as mes,
        sigla_uf,
        grupo_classe_consumo,
        count(*)                   as qtd_conexoes,
        sum(potencia_instalada_kw) as potencia_adicionada_kw
    from sistemas
    group by all
)

select
    grade.mes,
    year(grade.mes)  as ano,
    grade.mes > (select mes_referencia from periodo) as mes_provisorio,
    grade.sigla_uf,
    grade.nome_uf,
    grade.nome_regiao,
    grade.grupo_classe_consumo,
    coalesce(mensal.qtd_conexoes, 0)           as qtd_conexoes,
    cast(coalesce(mensal.potencia_adicionada_kw, 0) as double) as potencia_adicionada_kw,
    sum(coalesce(mensal.qtd_conexoes, 0)) over acumulado           as qtd_sistemas_acumulada,
    cast(sum(coalesce(mensal.potencia_adicionada_kw, 0)) over acumulado as double) as potencia_acumulada_kw
from grade
left join mensal using (mes, sigla_uf, grupo_classe_consumo)
window acumulado as (
    partition by grade.sigla_uf, grade.grupo_classe_consumo
    order by grade.mes
    rows between unbounded preceding and current row
)
order by grade.mes, grade.sigla_uf, grade.grupo_classe_consumo
