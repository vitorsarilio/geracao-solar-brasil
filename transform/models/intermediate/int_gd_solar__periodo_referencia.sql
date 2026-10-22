-- Uma linha com o período de referência usado por todos os marts.
--
-- A ANEEL publica com atraso, e as distribuidoras ainda cadastram conexões dos meses
-- recentes depois disso. Em outubro de 2026, por exemplo, agosto tinha só ~5% das conexões
-- de um mês normal, julho ~40% e junho ~70%. Usar esses meses faria qualquer região parecer
-- "desacelerando".
--
-- Por isso:
--   * ultimo_mes_fechado: último mês de calendário completo nos dados;
--   * mes_referencia: o último mês (até o último fechado) com pelo menos
--     `fracao_minima_mes_completo` das conexões médias dos 12 meses anteriores.
--     Os meses depois dele são provisórios.
-- As janelas de 12 meses da análise de aceleração terminam no mês de referência.

with sistemas as (
    select mes_conexao, data_conexao, data_publicacao_dados
    from {{ ref('int_gd_solar__empreendimentos') }}
),

ultima as (
    select
        max(data_conexao)          as ultima_data_conexao,
        max(data_publicacao_dados) as data_publicacao_dados
    from sistemas
),

fechado as (
    select
        *,
        cast(
            case
                when ultima_data_conexao = last_day(ultima_data_conexao)
                    then date_trunc('month', ultima_data_conexao)
                else date_trunc('month', ultima_data_conexao) - interval 1 month
            end
        as date) as ultimo_mes_fechado
    from ultima
),

mensal as (
    select mes_conexao as mes, count(*) as conexoes
    from sistemas
    where mes_conexao is not null
    group by all
),

com_media as (
    select
        mes,
        conexoes,
        avg(conexoes) over (order by mes rows between 12 preceding and 1 preceding) as media_12m_anteriores
    from mensal
),

completos as (
    select max(c.mes) as mes_referencia
    from com_media as c
    cross join fechado as f
    where c.mes <= f.ultimo_mes_fechado
      and c.conexoes >= {{ var('fracao_minima_mes_completo') }} * c.media_12m_anteriores
)

select
    f.data_publicacao_dados,
    f.ultima_data_conexao,
    f.ultimo_mes_fechado,
    c.mes_referencia,
    date_diff('month', c.mes_referencia, f.ultimo_mes_fechado) as qtd_meses_provisorios,
    -- janela recente: os 12 meses até o mês de referência (inclusive)
    cast(c.mes_referencia - interval 11 month as date) as inicio_janela_recente,
    -- janela anterior: os 12 meses imediatamente antes
    cast(c.mes_referencia - interval 23 month as date) as inicio_janela_anterior,
    cast(c.mes_referencia - interval 12 month as date) as fim_janela_anterior
from fechado as f
cross join completos as c
