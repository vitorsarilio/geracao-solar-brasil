-- A potência de cada sistema solar deve ser a mesma na relação principal e no arquivo técnico.
select
    t.cod_empreendimento,
    t.potencia_instalada_kw as potencia_tecnico,
    e.potencia_instalada_kw as potencia_relacao
from {{ ref('stg_aneel__gd_fotovoltaica_tecnico') }} as t
inner join {{ ref('stg_aneel__empreendimentos_gd') }} as e
    using (cod_empreendimento)
where abs(t.potencia_instalada_kw - e.potencia_instalada_kw) > 0.01
