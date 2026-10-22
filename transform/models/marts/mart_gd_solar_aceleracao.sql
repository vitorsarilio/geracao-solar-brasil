-- Pergunta 4: onde o crescimento está acelerando e onde está estabilizando.
--
-- Compara a potência conectada nos 12 meses até o mês de referência com os 12 meses
-- anteriores, para o Brasil, cada UF e cada município (limites em dbt_project.yml):
--   razão >= limite_acelerando     -> Acelerando
--   razão <= limite_desacelerando  -> Desacelerando
--   entre os dois                  -> Estável
-- Antes disso, dois filtros de qualidade:
--   * "Dados incompletos": UF com vários meses sem nenhuma conexão na janela recente
--     (indício de que a distribuidora parou de enviar dados), e os municípios dela;
--   * "Amostra pequena": município com poucas conexões em alguma das janelas.

with periodo as (
    select * from {{ ref('int_gd_solar__periodo_referencia') }}
),

sistemas as (
    select
        s.*,
        case
            when s.mes_conexao between p.inicio_janela_recente and p.mes_referencia then 'recente'
            when s.mes_conexao between p.inicio_janela_anterior and p.fim_janela_anterior then 'anterior'
        end as janela
    from {{ ref('int_gd_solar__empreendimentos') }} as s
    cross join periodo as p
),

lacunas_uf as (
    select
        sigla_uf,
        12 - count(distinct mes_conexao) filter (where janela = 'recente') as meses_sem_conexao_janela_recente
    from sistemas
    group by sigla_uf
),

{% set metricas %}
        count(*) filter (where janela = 'recente')                                 as conexoes_12m_recentes,
        count(*) filter (where janela = 'anterior')                                as conexoes_12m_anteriores,
        coalesce(sum(potencia_instalada_kw) filter (where janela = 'recente'), 0)  as potencia_12m_recentes_kw,
        coalesce(sum(potencia_instalada_kw) filter (where janela = 'anterior'), 0) as potencia_12m_anteriores_kw
{% endset %}

brasil as (
    select
        'Brasil' as nivel, null::varchar as sigla_uf, null::varchar as cod_municipio_ibge, 'Brasil' as nome,
        {{ metricas }}
    from sistemas
),

por_uf as (
    select
        'UF' as nivel, sigla_uf, null::varchar as cod_municipio_ibge, any_value(nome_uf) as nome,
        {{ metricas }}
    from sistemas
    group by sigla_uf
),

por_municipio as (
    select
        'Município' as nivel, s.sigla_uf, s.cod_municipio_ibge, any_value(m.nome_municipio) as nome,
        {{ metricas }}
    from sistemas as s
    left join {{ ref('stg_ibge__populacao_municipios') }} as m using (cod_municipio_ibge)
    group by s.sigla_uf, s.cod_municipio_ibge
),

todos as (
    select * from brasil
    union all select * from por_uf
    union all select * from por_municipio
),

com_razao as (
    select
        t.*,
        t.potencia_12m_recentes_kw / nullif(t.potencia_12m_anteriores_kw, 0) as razao_potencia,
        coalesce(l.meses_sem_conexao_janela_recente, 0) >= {{ var('meses_sem_conexao_para_lacuna') }} as uf_com_lacuna_de_dados
    from todos as t
    left join lacunas_uf as l using (sigla_uf)
)

select
    -- chave única da linha: código do município, sigla da UF ou "BR"
    coalesce(c.cod_municipio_ibge, c.sigla_uf, 'BR') as chave,
    c.nivel,
    c.sigla_uf,
    c.cod_municipio_ibge,
    c.nome,
    c.conexoes_12m_recentes,
    c.conexoes_12m_anteriores,
    cast(c.potencia_12m_recentes_kw as double) as potencia_12m_recentes_kw,
    cast(c.potencia_12m_anteriores_kw as double) as potencia_12m_anteriores_kw,
    c.razao_potencia,
    c.razao_potencia - 1 as variacao_potencia,
    -- Em municípios, uma única usina de minigeração (até 5 MW) move muito a potência;
    -- a variação no número de conexões ajuda a ler a tendência
    c.conexoes_12m_recentes * 1.0 / nullif(c.conexoes_12m_anteriores, 0) - 1 as variacao_conexoes,
    c.uf_com_lacuna_de_dados,
    case
        when c.uf_com_lacuna_de_dados then 'Dados incompletos'
        when c.nivel = 'Município'
            and least(c.conexoes_12m_recentes, c.conexoes_12m_anteriores) < {{ var('minimo_conexoes_por_janela') }}
            then 'Amostra pequena'
        when c.razao_potencia >= {{ var('limite_acelerando') }} then 'Acelerando'
        when c.razao_potencia <= {{ var('limite_desacelerando') }} then 'Desacelerando'
        else 'Estável'
    end as classificacao,
    p.inicio_janela_recente,
    p.mes_referencia        as fim_janela_recente,
    p.inicio_janela_anterior,
    p.fim_janela_anterior
from com_razao as c
cross join periodo as p
order by
    case c.nivel when 'Brasil' then 1 when 'UF' then 2 else 3 end,
    c.sigla_uf nulls first,
    c.cod_municipio_ibge nulls first
