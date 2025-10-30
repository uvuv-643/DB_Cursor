import openai



user_promt = "покупатели и количество проданных продуктов в заказах с товарами с высотой больше 9 и весом больше 1500"

tables = """
TABLE main.customers
-------------------
  COLUMNS:
    - customer_id TEXT
    - customer_unique_id TEXT
    - customer_zip_code_prefix INTEGER
    - customer_city TEXT
    - customer_state TEXT

TABLE main.orders
----------------
  COLUMNS:
    - order_id TEXT
    - customer_id TEXT
    - order_status TEXT
    - order_purchase_timestamp TEXT
    - order_approved_at TEXT
    - order_delivered_carrier_date TEXT
    - order_delivered_customer_date TEXT
    - order_estimated_delivery_date TEXT
"""


client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project= YANDEX_CLOUD_FOLDER
)

response = client.responses.create(
    model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
    input=
    f"""Проанализируй структуру таблиц и список их колонок.
Твоя задача — выбрать наиболее важные и информативные колонки для дальнейшего визуального анализа данных.

Для каждой выбранной колонки укажи, какой тип визуализации наиболее подходит для анализа этой колонки.

Используй следующие типы визуализаций (только из этого списка):

bar — категориальные сравнения (например, города, статусы)

line — временные ряды, динамика

map — географическое распределение

pie — доли и категории

hist — распределения числовых значений

Укажи только основные колонки, которые реально пригодны для визуализации, исключая технические или дублирующие поля.

Формат ответа:

TABLE <имя таблицы>
--------------------
Важные колонки:
- <название_колонки> — <тип визуализации из списка>


Пример входных данных:

<example start>
TABLE main.customers
-------------------
  COLUMNS:
    - customer_id TEXT
    - customer_unique_id TEXT
    - customer_zip_code_prefix INTEGER
    - customer_city TEXT
    - customer_state TEXT

TABLE main.orders
----------------
  COLUMNS:
    - order_id TEXT
    - customer_id TEXT
    - order_status TEXT
    - order_purchase_timestamp TEXT
    - order_approved_at TEXT
    - order_delivered_carrier_date TEXT
    - order_delivered_customer_date TEXT
    - order_estimated_delivery_date TEXT
  <example end>


Пример выходных данных:

<example start>
TABLE main.customers
--------------------
Важные колонки:
- customer_city — bar
- customer_state — map

TABLE main.orders
----------------
Важные колонки:
- order_status — bar
- order_purchase_timestamp — line
- order_delivered_customer_date — line
- order_estimated_delivery_date — line
<example end>


Цель — определить основные аналитически значимые колонки и тип визуализации, который лучше всего подходит для их анализа.

Вот список колонок, который тебе необходимо обработать:
{tables}
    """,
    
    temperature=0.8,
    max_output_tokens=1500
)
print(response.output[0].content[0].text)