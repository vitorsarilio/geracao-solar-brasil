-- O mart de aceleração precisa ter exatamente 1 linha de Brasil e 27 de UF.
select nivel, count(*) as linhas
from {{ ref('mart_gd_solar_aceleracao') }}
where nivel in ('Brasil', 'UF')
group by nivel
having (nivel = 'Brasil' and count(*) <> 1)
    or (nivel = 'UF' and count(*) <> 27)
