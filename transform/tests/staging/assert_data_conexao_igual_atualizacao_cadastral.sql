-- Hoje a data de conexão (arquivo técnico) é idêntica à data de atualização cadastral
-- (relação principal) em 100% dos registros. Se começarem a divergir, a semântica da
-- fonte mudou e vale revisar qual data usar na série histórica. Só avisa, não falha.
{{ config(severity='warn') }}

select
    t.cod_empreendimento,
    t.data_conexao,
    e.data_atualizacao_cadastral
from {{ ref('stg_aneel__gd_fotovoltaica_tecnico') }} as t
inner join {{ ref('stg_aneel__empreendimentos_gd') }} as e
    using (cod_empreendimento)
where t.data_conexao is distinct from e.data_atualizacao_cadastral
