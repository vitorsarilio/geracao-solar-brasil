---
title: Estados
sidebar_position: 1
---

```sql ufs
select
    *,
    potencia_kw / 1e3 as potencia_mw,
    potencia_kw / 1e6 as potencia_gw
from gd.uf
order by potencia_kw desc
```

```sql lider_absoluto
select * from ${ufs} order by ranking_potencia limit 1
```

```sql lider_per_capita
select * from ${ufs} order by ranking_per_capita limit 1
```

```sql top5
select sum(participacao_potencia) as participacao from (select * from ${ufs} order by ranking_potencia limit 5)
```

## 2. Quais estados concentram mais geração?

**<Value data={lider_absoluto} column=nome_uf />** tem a maior potência instalada (<Value data={lider_absoluto} column=potencia_gw fmt='#,##0.0' /> GW, <Value data={lider_absoluto} column=participacao_potencia fmt=pct0 /> do país), e os 5 maiores estados somam <Value data={top5} column=participacao fmt=pct0 /> do total. Mas o tamanho da população muda o quadro: por habitante, quem lidera é **<Value data={lider_per_capita} column=nome_uf />**, com <Value data={lider_per_capita} column=watts_por_habitante fmt='#,##0' /> W por habitante.

<Tabs>
<Tab label="Potência instalada">

<AreaMap
    data={ufs}
    areaCol=cod_uf_ibge
    geoJsonUrl="/geracao-solar-brasil/br-ufs.geojson"
    geoId=codarea
    value=potencia_mw
    valueFmt='#,##0" MW"'
    tooltip={[
        {id: 'nome_uf', showColumnName: false, valueClass: 'font-bold'},
        {id: 'potencia_mw', fieldClass: 'text-[grey]', valueFmt: '#,##0" MW"', title: 'Potência'},
        {id: 'qtd_sistemas', fieldClass: 'text-[grey]', valueFmt: '#,##0', title: 'Sistemas'}
    ]}
    height=420
    basemap={`https://tile.openstreetmap.org/{z}/{x}/{y}.png`}
    attribution="© OpenStreetMap"
/>

</Tab>
<Tab label="Por habitante">

<AreaMap
    data={ufs}
    areaCol=cod_uf_ibge
    geoJsonUrl="/geracao-solar-brasil/br-ufs.geojson"
    geoId=codarea
    value=watts_por_habitante
    valueFmt='#,##0" W/hab."'
    tooltip={[
        {id: 'nome_uf', showColumnName: false, valueClass: 'font-bold'},
        {id: 'watts_por_habitante', fieldClass: 'text-[grey]', valueFmt: '#,##0" W"', title: 'Por habitante'},
        {id: 'populacao', fieldClass: 'text-[grey]', valueFmt: '#,##0', title: 'População'}
    ]}
    height=420
    basemap={`https://tile.openstreetmap.org/{z}/{x}/{y}.png`}
    attribution="© OpenStreetMap"
/>

</Tab>
</Tabs>

<BarChart
    data={ufs}
    x=sigla_uf
    y=potencia_mw
    series=nome_regiao
    yFmt='#,##0" MW"'
    sort=false
    title="Potência instalada por estado"
    yAxisTitle="MW"
/>

```sql ufs_per_capita
select * from ${ufs} order by watts_por_habitante desc
```

<BarChart
    data={ufs_per_capita}
    x=sigla_uf
    y=watts_por_habitante
    series=nome_regiao
    yFmt='#,##0" W"'
    sort=false
    title="Potência por habitante (watts)"
    subtitle="kW instalados por 1.000 habitantes; população estimada pelo IBGE"
/>

<DataTable data={ufs} rows=27>
    <Column id=nome_uf title="Estado" />
    <Column id=nome_regiao title="Região" />
    <Column id=potencia_mw title="Potência (MW)" fmt='#,##0' contentType=bar />
    <Column id=participacao_potencia title="% do país" fmt=pct1 />
    <Column id=qtd_sistemas title="Sistemas" fmt='#,##0' />
    <Column id=potencia_media_kw title="kW por sistema" fmt='#,##0.0' />
    <Column id=watts_por_habitante title="W por habitante" fmt='#,##0' contentType=colorscale />
    <Column id=ranking_per_capita title="Ranking per capita" />
</DataTable>
