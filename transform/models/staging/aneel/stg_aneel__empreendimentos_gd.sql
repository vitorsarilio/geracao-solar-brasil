-- Um registro por empreendimento de geração distribuída (todas as fontes).
-- Fora daqui: colunas que a ANEEL descontinuou (CodSubGrupoTarifario e
-- SigModalidadeEmpreendimento vêm 100% nulas) e as de subestação (>99,9% nulas).

with fonte as (
    select * from {{ source('aneel', 'aneel_empreendimentos_gd') }}
)

select
    {{ texto('CodEmpreendimento') }}                      as cod_empreendimento,

    -- distribuidora
    {{ texto('NumCNPJDistribuidora') }}                   as cnpj_distribuidora,
    {{ texto('SigAgente') }}                              as sigla_distribuidora,
    {{ texto('NomAgente') }}                              as nome_distribuidora,

    -- localização
    {{ texto('SigUF') }}                                  as sigla_uf,
    {{ texto('CodUFibge') }}                              as cod_uf_ibge,
    -- a fonte escreve "Centro Oeste"; o nome oficial do IBGE tem hífen
    replace({{ texto('NomRegiao') }}, 'Centro Oeste', 'Centro-Oeste') as nome_regiao,
    {{ texto('CodMunicipioIbge') }}                       as cod_municipio_ibge,
    {{ texto('NomMunicipio') }}                           as nome_municipio,

    -- consumidor
    {{ texto('CodClasseConsumo') }}                       as cod_classe_consumo,
    {{ texto('DscSubGrupoTarifario') }}                   as subgrupo_tarifario,
    {{ texto('SigTipoConsumidor') }}                      as tipo_consumidor,
    {{ texto('DscModalidadeHabilitado') }}                as modalidade,
    cast({{ texto('QtdUCRecebeCredito') }} as integer)    as qtd_uc_recebe_credito,

    -- geração
    {{ texto('SigTipoGeracao') }}                         as sigla_tipo_geracao,
    {{ texto('DscFonteGeracao') }}                        as fonte_geracao,
    {{ texto('DscPorte') }}                               as porte,
    {{ numero_br('MdaPotenciaInstaladaKW') }}             as potencia_instalada_kw,

    -- datas
    {{ data_valida('DthAtualizaCadastralEmpreend') }}     as data_atualizacao_cadastral,
    cast(DatGeracaoConjuntoDados as date)                 as data_publicacao_dados

from fonte
