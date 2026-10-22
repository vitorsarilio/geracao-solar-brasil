{#
  Conversões usadas no staging. O dado bruto chega todo como texto, fiel à fonte.
#}

{#
  Número no formato brasileiro ("32,50"). Falha se o valor não for numérico.
  Use tipo='decimal(12,2)' para valores que serão somados: soma de decimal é exata e não
  depende da ordem (com double, a soma paralela varia nas últimas casas a cada execução,
  e os Parquet dos marts mudariam sem o dado mudar).
#}
{% macro numero_br(coluna, tipo='double') -%}
    cast(replace(trim({{ coluna }}), ',', '.') as {{ tipo }})
{%- endmacro %}


{# Texto limpo: tira espaços das pontas e transforma vazio em nulo. #}
{% macro texto(coluna) -%}
    nullif(trim({{ coluna }}), '')
{%- endmacro %}


{#
  Data ISO ("2026-08-31"). A ANEEL usa 1900-01-01 como valor de preenchimento para
  data desconhecida; datas anteriores a `minima` viram nulo.
#}
{% macro data_valida(coluna, minima='2000-01-01') -%}
    case
        when cast({{ coluna }} as date) < date '{{ minima }}' then null
        else cast({{ coluna }} as date)
    end
{%- endmacro %}
