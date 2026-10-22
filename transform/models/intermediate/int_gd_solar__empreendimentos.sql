-- Um registro por sistema solar fotovoltaico (UFV) de geração distribuída, com a data de
-- conexão (do arquivo técnico) e a classe de consumo já rotulada.
-- Materializado como tabela porque todos os marts partem daqui (~4,7 milhões de linhas).
{{ config(materialized='table') }}

with empreendimentos as (
    select *
    from {{ ref('stg_aneel__empreendimentos_gd') }}
    where sigla_tipo_geracao = 'UFV'
),

tecnico as (
    select cod_empreendimento, data_conexao
    from {{ ref('stg_aneel__gd_fotovoltaica_tecnico') }}
),

classes as (
    select * from {{ ref('classes_consumo') }}
),

ufs as (
    select * from {{ ref('ufs') }}
)

select
    e.cod_empreendimento,

    t.data_conexao,
    cast(date_trunc('month', t.data_conexao) as date) as mes_conexao,
    year(t.data_conexao)                              as ano_conexao,

    e.sigla_uf,
    u.nome_uf,
    u.nome_regiao,
    e.cod_municipio_ibge,

    e.cod_classe_consumo,
    c.classe_consumo,
    c.grupo_classe_consumo,

    e.tipo_consumidor,
    e.porte,
    e.modalidade,
    e.potencia_instalada_kw,
    e.data_publicacao_dados

from empreendimentos as e
left join tecnico as t using (cod_empreendimento)
left join classes as c using (cod_classe_consumo)
left join ufs as u using (sigla_uf)
