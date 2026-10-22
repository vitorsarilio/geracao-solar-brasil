---
title: Geração distribuída solar no Brasil
---

<!--
  Datas: o navegador converte datas para o fuso local (UTC−3), o que mostraria o dia
  anterior. Por isso as datas de texto são formatadas no SQL, e os meses dos gráficos
  ficam ao meio-dia do dia 1.
-->

```sql resumo
select
    *,
    potencia_kw / 1e6                              as potencia_gw,
    strftime(data_publicacao_dados, '%d/%m/%Y')    as data_publicacao_txt,
    strftime(ultima_data_conexao, '%d/%m/%Y')      as ultima_conexao_txt,
    strftime(mes_referencia, '%m/%Y')              as mes_referencia_txt
from gd.resumo
```

```sql crescimento_mensal
select
    mes + interval 12 hour             as mes,
    sum(potencia_acumulada_kw) / 1e6  as potencia_acumulada_gw,
    sum(potencia_adicionada_kw) / 1e3 as potencia_adicionada_mw,
    case when bool_or(mes_provisorio) then 'Provisório' else 'Consolidado' end as situacao
from gd.mensal
where mes >= '2015-01-01'
group by mes
order by mes
```

```sql crescimento_anual
select
    cast(cast(ano as integer) as varchar) as ano,
    sum(potencia_adicionada_kw) / 1e3 as potencia_adicionada_mw,
    cast(sum(qtd_conexoes) as bigint)  as conexoes,
    case
        when bool_or(mes_provisorio) or max(month(mes)) < 12 then 'Ano incompleto'
        else 'Ano completo'
    end as situacao
from gd.mensal
where ano >= 2015
group by ano
order by ano
```

```sql ano_pico
select ano, potencia_adicionada_mw / 1e3 as potencia_adicionada_gw
from ${crescimento_anual}
where situacao = 'Ano completo'
order by potencia_adicionada_mw desc
limit 1
```

```sql acumulado_regiao
select
    mes + interval 12 hour           as mes,
    nome_regiao,
    sum(potencia_acumulada_kw) / 1e6 as potencia_acumulada_gw
from gd.mensal
where mes >= '2015-01-01'
group by all
order by mes, nome_regiao
```

Painel sobre a **micro e minigeração distribuída (MMGD) solar fotovoltaica**: sistemas em telhados, terrenos e fachadas de casas, comércios, propriedades rurais e indústrias que geram a própria energia e se conectam à rede da distribuidora. Os dados são abertos, publicados pela ANEEL, e o painel é atualizado automaticamente toda semana.

<BigValue data={resumo} value=potencia_gw title="Potência instalada" fmt='#,##0.0" GW"' />
<BigValue data={resumo} value=qtd_sistemas title="Sistemas conectados" fmt='#,##0' />
<BigValue data={resumo} value=qtd_municipios_com_gd_solar title="Municípios com GD solar" fmt='#,##0' />
<BigValue data={resumo} value=watts_por_habitante title="Watts por habitante" fmt='#,##0' />

<Alert status="info">

Dados da ANEEL publicados em **<Value data={resumo} column=data_publicacao_txt />**, com conexões até **<Value data={resumo} column=ultima_conexao_txt />**. As distribuidoras cadastram parte das conexões com atraso, então os **<Value data={resumo} column=qtd_meses_provisorios />** meses mais recentes ainda estão incompletos e aparecem como *provisórios*. O mês de referência para comparações é **<Value data={resumo} column=mes_referencia_txt />**. [Como isso é calculado](/metodologia).

</Alert>

## 1. Como a potência instalada cresceu?

O Brasil soma **<Value data={resumo} column=potencia_gw fmt='#,##0.0' /> GW** de geração distribuída solar. O ano com mais potência conectada foi **<Value data={ano_pico} column=ano />**, com <Value data={ano_pico} column=potencia_adicionada_gw fmt='#,##0.0' /> GW novos.

<LineChart
    data={crescimento_mensal}
    x=mes
    y=potencia_acumulada_gw
    yFmt='#,##0.0" GW"'
    title="Potência instalada acumulada"
/>

<BarChart
    data={crescimento_anual}
    x=ano
    y=potencia_adicionada_mw
    series=situacao
    sort=false
    yFmt='#,##0" MW"'
    title="Potência conectada por ano"
    colorPalette={['#e8890c', '#f6d27a']}
/>

<BarChart
    data={crescimento_mensal}
    x=mes
    y=potencia_adicionada_mw
    series=situacao
    yFmt='#,##0" MW"'
    title="Potência conectada por mês"
    subtitle="Meses provisórios ainda recebem cadastros atrasados"
    colorPalette={['#e8890c', '#f6d27a']}
/>

<AreaChart
    data={acumulado_regiao}
    x=mes
    y=potencia_acumulada_gw
    series=nome_regiao
    yFmt='#,##0.0" GW"'
    title="Potência acumulada por região"
/>

## Explore as outras perguntas

- [**Estados**](/estados) e [**municípios**](/municipios): onde a geração está concentrada, em valor absoluto e por habitante.
- [**Classes de consumo**](/classes-de-consumo): residencial, comercial, rural, industrial...
- [**Aceleração**](/aceleracao): onde o ritmo de novas conexões está crescendo e onde está estabilizando.
- [**Metodologia**](/metodologia): fontes, definições e limitações.
