-- Um registro por empreendimento fotovoltaico, com a data de conexão e dados dos equipamentos.

with fonte as (
    select * from {{ source('aneel', 'aneel_gd_fotovoltaica_tecnico') }}
)

select
    {{ texto('CodGeracaoDistribuida') }}                  as cod_empreendimento,
    {{ data_valida('DatConexao') }}                       as data_conexao,

    {{ numero_br('MdaPotenciaInstalada', 'decimal(12,2)') }}             as potencia_instalada_kw,
    {{ numero_br('MdaPotenciaModulos') }}                 as potencia_modulos_kw,
    {{ numero_br('MdaPotenciaInversores') }}              as potencia_inversores_kw,
    {{ numero_br('MdaAreaArranjo') }}                     as area_arranjo_m2,
    cast({{ texto('QtdModulos') }} as integer)            as qtd_modulos,

    {{ texto('NomFabricanteModulo') }}                    as fabricante_modulo,
    {{ texto('NomModeloModulo') }}                        as modelo_modulo,
    {{ texto('NomFabricanteInversor') }}                  as fabricante_inversor,
    {{ texto('NomModeloInversor') }}                      as modelo_inversor,

    cast(DatGeracaoConjuntoDados as date)                 as data_publicacao_dados

from fonte
