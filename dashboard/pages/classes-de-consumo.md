---
title: Classes
sidebar_position: 3
---

```sql grupos_total
select
    grupo_classe_consumo,
    sum(potencia_adicionada_kw) / 1e6 as potencia_gw,
    cast(sum(qtd_conexoes) as bigint)  as sistemas,
    sum(potencia_adicionada_kw) / cast(sum(qtd_conexoes) as bigint) as potencia_media_kw,
    sum(potencia_adicionada_kw) / sum(sum(potencia_adicionada_kw)) over () as participacao
from gd.classe_anual
group by grupo_classe_consumo
order by potencia_gw desc
```

```sql lider
select * from ${grupos_total} limit 1
```

```sql grupos_por_ano
select
    cast(cast(ano as integer) as varchar) as ano,
    grupo_classe_consumo,
    sum(potencia_adicionada_kw) / 1e3 as potencia_mw
from gd.classe_anual
where ano >= 2016
group by all
order by ano, grupo_classe_consumo
```

```sql classes_detalhe
select
    classe_consumo,
    grupo_classe_consumo,
    cast(sum(qtd_conexoes) as bigint)  as sistemas,
    sum(potencia_adicionada_kw) / 1e3 as potencia_mw,
    sum(potencia_adicionada_kw) / cast(sum(qtd_conexoes) as bigint) as potencia_media_kw
from gd.classe_anual
group by all
order by potencia_mw desc
```

## 3. Como a geração se divide por classe de consumo?

A classe **<Value data={lider} column=grupo_classe_consumo />** responde por <Value data={lider} column=participacao fmt=pct0 /> da potência instalada. Os sistemas residenciais são pequenos (poucos kW cada) mas muito numerosos; os comerciais, rurais e industriais são menos frequentes e bem maiores.


<BarChart
    data={grupos_total}
    x=grupo_classe_consumo
    y=potencia_gw
    swapXY=true
    sort=false
    yFmt='#,##0.0" GW"'
    title="Potência instalada por classe"
/>

<BarChart
    data={grupos_total}
    x=grupo_classe_consumo
    y=potencia_media_kw
    swapXY=true
    sort=false
    yFmt='#,##0.0" kW"'
    title="Tamanho médio do sistema"
/>


<BarChart
    data={grupos_por_ano}
    x=ano
    y=potencia_mw
    series=grupo_classe_consumo
    type=stacked100
    title="Participação de cada classe na potência conectada no ano"
    subtitle="O último ano ainda está incompleto"
/>

<DataTable data={classes_detalhe} rows=12>
    <Column id=classe_consumo title="Classe" />
    <Column id=grupo_classe_consumo title="Grupo" />
    <Column id=sistemas title="Sistemas" fmt='#,##0' />
    <Column id=potencia_mw title="Potência (MW)" fmt='#,##0' contentType=bar />
    <Column id=potencia_media_kw title="kW por sistema" fmt='#,##0.0' />
</DataTable>

<Details title="Sobre a classe REBR">

A ANEEL publica a classe `REBR` sem descrição, nem no arquivo nem no dicionário de dados. Ela foi agrupada em **Residencial** porque 99% desses sistemas estão no subgrupo tarifário B1 (residencial), são de pessoa física e têm o mesmo tamanho médio da classe residencial (cerca de 7 kW).

</Details>
