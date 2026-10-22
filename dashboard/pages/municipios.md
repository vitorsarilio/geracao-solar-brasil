---
title: Municípios
sidebar_position: 2
---

```sql lista_ufs
select sigla_uf, nome_uf from gd.uf order by nome_uf
```

<Dropdown data={lista_ufs} name=uf value=sigla_uf label=nome_uf title="Estado">
    <DropdownOption value="%" valueLabel="Todo o Brasil" />
</Dropdown>

<ButtonGroup name=populacao_minima title="População mínima (ranking per capita)">
    <ButtonGroupItem valueLabel="Todos" value=0 />
    <ButtonGroupItem valueLabel="20 mil+" value=20000 default />
    <ButtonGroupItem valueLabel="100 mil+" value=100000 />
    <ButtonGroupItem valueLabel="500 mil+" value=500000 />
</ButtonGroup>

```sql municipios
select
    nome_municipio || ' (' || sigla_uf || ')' as municipio,
    nome_municipio,
    sigla_uf,
    populacao,
    qtd_sistemas,
    potencia_kw / 1e3 as potencia_mw,
    potencia_media_kw,
    watts_por_habitante,
    ranking_potencia_uf
from gd.municipio
where sigla_uf like '${inputs.uf.value}'
```

```sql top_absoluto
select * from ${municipios} order by potencia_mw desc limit 15
```

```sql top_per_capita
select * from ${municipios}
where populacao >= ${inputs.populacao_minima}
order by watts_por_habitante desc
limit 15
```

```sql sem_gd
select count(*) filter (where qtd_sistemas = 0) as sem_gd, count(*) as total from ${municipios}
```

## 2. Quais municípios concentram mais geração?

Em valor absoluto, as capitais e as grandes cidades do agronegócio aparecem no topo. Por habitante, o destaque vai para cidades médias, onde a geração solar se espalhou por residências e propriedades rurais. Só <Value data={sem_gd} column=sem_gd /> de <Value data={sem_gd} column=total fmt='#,##0' /> municípios da seleção não têm nenhum sistema.


<BarChart
    data={top_absoluto}
    x=municipio
    y=potencia_mw
    swapXY=true
    sort=false
    yFmt='#,##0" MW"'
    title="Maior potência instalada"
/>

<BarChart
    data={top_per_capita}
    x=municipio
    y=watts_por_habitante
    swapXY=true
    sort=false
    yFmt='#,##0" W"'
    title="Maior potência por habitante"
    subtitle="Filtrado pela população mínima escolhida acima"
/>


### Todos os municípios

<DataTable data={municipios} search=true rows=20 sort="potencia_mw desc">
    <Column id=nome_municipio title="Município" />
    <Column id=sigla_uf title="UF" />
    <Column id=populacao title="População" fmt='#,##0' />
    <Column id=qtd_sistemas title="Sistemas" fmt='#,##0' />
    <Column id=potencia_mw title="Potência (MW)" fmt='#,##0.0' contentType=bar />
    <Column id=potencia_media_kw title="kW por sistema" fmt='#,##0.0' />
    <Column id=watts_por_habitante title="W por habitante" fmt='#,##0' contentType=colorscale />
    <Column id=ranking_potencia_uf title="Posição no estado" />
</DataTable>
