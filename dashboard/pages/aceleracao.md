---
title: Aceleração
sidebar_position: 4
---

```sql brasil
select *, strftime(fim_janela_recente, '%m/%Y') as fim_janela_txt from gd.aceleracao where nivel = 'Brasil'
```

```sql ufs
select
    *,
    potencia_12m_recentes_kw / 1e3  as potencia_recente_mw,
    potencia_12m_anteriores_kw / 1e3 as potencia_anterior_mw
from gd.aceleracao
where nivel = 'UF'
order by variacao_potencia desc
```

```sql contagem_ufs
select classificacao, count(*) as estados
from ${ufs}
group by classificacao
order by estados desc
```

## 4. Onde o crescimento está acelerando e onde está estabilizando?

A comparação é entre a potência conectada nos **12 meses até <Value data={brasil} column=fim_janela_txt />** e nos **12 meses anteriores**. No Brasil como um todo, a variação foi de **<Value data={brasil} column=variacao_potencia fmt=pct1 />**, o que classifica o país como **<Value data={brasil} column=classificacao />**.

<Alert status="info">

**Como ler:** razão de pelo menos 1,2 (+20%) é *Acelerando*; até 0,8 (−20%) é *Desacelerando*; entre os dois, *Estável*. Estados com vários meses sem nenhuma conexão registrada na janela recente aparecem como *Dados incompletos*, porque o mais provável é que a distribuidora tenha parado de enviar os dados, não que o mercado tenha parado.

</Alert>

<BarChart
    data={ufs}
    x=sigla_uf
    y=variacao_potencia
    series=classificacao
    yFmt=pct0
    sort=false
    title="Variação da potência conectada: últimos 12 meses contra os 12 anteriores"
    colorPalette={['#2f855a', '#8d99ae', '#c53030', '#b7791f']}
/>

<DataTable data={ufs} rows=27>
    <Column id=nome title="Estado" />
    <Column id=potencia_anterior_mw title="MW (12 meses anteriores)" fmt='#,##0' />
    <Column id=potencia_recente_mw title="MW (12 meses recentes)" fmt='#,##0' />
    <Column id=variacao_potencia title="Variação da potência" fmt=pct1 contentType=delta />
    <Column id=variacao_conexoes title="Variação das conexões" fmt=pct1 contentType=delta />
    <Column id=classificacao title="Tendência" />
</DataTable>

### Municípios

```sql opcoes_classificacao
select distinct classificacao from gd.aceleracao where nivel = 'Município' order by classificacao
```

```sql lista_ufs
select sigla_uf, nome_uf from gd.uf order by nome_uf
```

<Dropdown data={opcoes_classificacao} name=classificacao value=classificacao title="Tendência" defaultValue="Acelerando">
    <DropdownOption value="%" valueLabel="Todas" />
</Dropdown>

<Dropdown data={lista_ufs} name=uf value=sigla_uf label=nome_uf title="Estado">
    <DropdownOption value="%" valueLabel="Todo o Brasil" />
</Dropdown>

```sql municipios
select
    nome,
    sigla_uf,
    conexoes_12m_anteriores,
    conexoes_12m_recentes,
    potencia_12m_anteriores_kw / 1e3 as potencia_anterior_mw,
    potencia_12m_recentes_kw / 1e3   as potencia_recente_mw,
    variacao_potencia,
    variacao_conexoes,
    classificacao
from gd.aceleracao
where nivel = 'Município'
  and classificacao like '${inputs.classificacao.value}'
  and sigla_uf like '${inputs.uf.value}'
order by conexoes_12m_recentes desc
```

```sql contagem_municipios
select classificacao, count(*) as municipios
from gd.aceleracao
where nivel = 'Município' and sigla_uf like '${inputs.uf.value}'
group by classificacao
order by municipios desc
```

<BarChart
    data={contagem_municipios}
    x=classificacao
    y=municipios
    swapXY=true
    title="Municípios por tendência"
    subtitle="Municípios com menos de 50 conexões em alguma das janelas ficam como Amostra pequena"
/>

<DataTable data={municipios} search=true rows=20>
    <Column id=nome title="Município" />
    <Column id=sigla_uf title="UF" />
    <Column id=conexoes_12m_anteriores title="Conexões (anteriores)" fmt='#,##0' />
    <Column id=conexoes_12m_recentes title="Conexões (recentes)" fmt='#,##0' />
    <Column id=variacao_conexoes title="Variação das conexões" fmt=pct0 contentType=delta />
    <Column id=variacao_potencia title="Variação da potência" fmt=pct0 contentType=delta />
    <Column id=classificacao title="Tendência" />
</DataTable>

<Details title="Por que mostrar conexões e potência?">

A classificação usa a potência. Em municípios, porém, uma única usina de minigeração (até 5 MW) pode mover muito o total. Quando a potência sobe mas o número de conexões cai, o crescimento vem de poucos sistemas grandes, não de uma adoção mais ampla.

</Details>
