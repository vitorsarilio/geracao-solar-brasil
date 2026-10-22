-- O par (sigla, código IBGE) da UF na ANEEL precisa bater com a seed `ufs`
-- (o mapa do dashboard liga os dados à malha do IBGE pelo código).
select distinct e.sigla_uf, e.cod_uf_ibge as cod_aneel, u.cod_uf_ibge as cod_seed
from {{ ref('stg_aneel__empreendimentos_gd') }} as e
left join {{ ref('ufs') }} as u using (sigla_uf)
where e.cod_uf_ibge is distinct from u.cod_uf_ibge
