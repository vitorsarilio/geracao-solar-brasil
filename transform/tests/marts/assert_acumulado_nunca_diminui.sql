-- A potência e a quantidade acumuladas nunca podem diminuir de um mês para o seguinte
-- (em cada UF × grupo de classe). Retorna os pontos onde diminuem.

with serie as (
    select
        mes,
        sigla_uf,
        grupo_classe_consumo,
        potencia_acumulada_kw,
        qtd_sistemas_acumulada,
        lag(potencia_acumulada_kw) over janela  as potencia_mes_anterior,
        lag(qtd_sistemas_acumulada) over janela as qtd_mes_anterior
    from {{ ref('fct_gd_solar_mensal') }}
    window janela as (partition by sigla_uf, grupo_classe_consumo order by mes)
)

select *
from serie
where potencia_acumulada_kw < potencia_mes_anterior - 0.001
   or qtd_sistemas_acumulada < qtd_mes_anterior
