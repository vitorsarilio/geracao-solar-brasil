---
title: Metodologia
sidebar_position: 5
---

```sql resumo
select *, strftime(mes_referencia, '%m/%Y') as mes_referencia_txt from gd.resumo
```

## Fontes

| Fonte | Conteúdo | Licença |
|---|---|---|
| [ANEEL – Relação de Empreendimentos de Geração Distribuída](https://dadosabertos.aneel.gov.br/dataset/relacao-de-empreendimentos-de-geracao-distribuida) | Cada sistema de micro e minigeração distribuída: UF, município, classe de consumo, fonte e potência. A data de conexão vem do arquivo técnico de fotovoltaica do mesmo conjunto. | ODbL |
| [IBGE – SIDRA, tabela 6579](https://sidra.ibge.gov.br/tabela/6579) | Estimativa da população residente por município (<Value data={resumo} column=ano_populacao fmt='0' />). | Dados públicos |
| [IBGE – Malhas territoriais](https://servicodados.ibge.gov.br/api/docs/malhas) | Contorno dos estados usado nos mapas. | Dados públicos |

Só entram sistemas **solares fotovoltaicos** (tipo UFV), que são mais de 99,9% da geração distribuída no país.

## Definições

- **Potência instalada:** soma da potência nominal dos sistemas, em kW (1 MW = 1.000 kW; 1 GW = 1.000.000 kW).
- **Watts por habitante:** potência instalada dividida pela população. É o mesmo número que "kW por 1.000 habitantes".
- **Mês de referência:** último mês considerado completo. As distribuidoras cadastram parte das conexões com atraso; em outubro de 2026, por exemplo, agosto tinha só ~5% das conexões de um mês normal. O mês de referência é o mais recente com pelo menos 80% da média de conexões dos 12 meses anteriores; os meses seguintes aparecem como *provisórios*. Hoje ele é **<Value data={resumo} column=mes_referencia_txt />**.
- **Aceleração:** potência conectada nos 12 meses até o mês de referência, dividida pela dos 12 meses anteriores. Acima de 1,2 é *Acelerando*; abaixo de 0,8, *Desacelerando*; entre os dois, *Estável*.

## Limitações

- **Atraso de cadastro:** os números dos meses mais recentes ainda vão crescer nas próximas publicações.
- **Lacunas por distribuidora:** quando uma distribuidora para de enviar dados, o estado inteiro parece parado. Esses casos aparecem como *Dados incompletos* na página de aceleração.
- **Data de conexão:** <Value data={resumo} column=qtd_sistemas_sem_data_conexao /> sistemas vêm com uma data de preenchimento (01/01/1900); eles contam nos totais, mas ficam fora das séries por mês e por ano.
- **Classe REBR:** publicada sem descrição pela ANEEL; agrupada em Residencial (detalhes na página de classes).
- **Formato dos números:** o Evidence formata números no padrão americano (ponto como separador decimal).

## Privacidade

A base da ANEEL traz CPF/CNPJ, nome do titular e CEP. Essas colunas são descartadas já na ingestão, antes de qualquer arquivo ser gravado, e os dados publicados são sempre agregados no mínimo por município.

## Como o painel é feito

Toda semana, um workflow do GitHub Actions baixa os dados (Python), modela as tabelas com dbt + DuckDB (com testes de qualidade), gera este site com Evidence.dev e publica no GitHub Pages, com custo zero. O código está em [github.com/vitorsarilio/geracao-solar-brasil](https://github.com/vitorsarilio/geracao-solar-brasil).
