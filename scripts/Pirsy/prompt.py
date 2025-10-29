import openai

YANDEX_CLOUD_MODEL = ""
YANDEX_CLOUD_FOLDER = ""
YANDEX_CLOUD_API_KEY = ""

user_promt = "покупатели и количество проданных продуктов в заказах с товарами с высотой больше 9 и весом больше 1500"


client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project= YANDEX_CLOUD_FOLDER
)

response = client.responses.create(
    model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
    input=
    f"""Раздели данный запрос на несколько связанных по смыслу фрагментов: {user_promt}. В ответе перечисляй только фрагменты из текста, разделённые "//" После каждого запроса в скобках реализуй sql запрос для этого фрагмента (Все фрагменты должны быть частью одного sql запроса). В конце объедени все sql фрагменты
    SCHEMA main
===========

TABLE main.customers
-------------------
  COLUMNS:
    - customer_id TEXT
    - customer_unique_id TEXT
    - customer_zip_code_prefix INTEGER
    - customer_city TEXT
    - customer_state TEXT


TABLE main.geolocation
---------------------
  COLUMNS:
    - geolocation_zip_code_prefix INTEGER
    - geolocation_lat REAL
    - geolocation_lng REAL
    - geolocation_city TEXT
    - geolocation_state TEXT


TABLE main.leads_closed
----------------------
  COLUMNS:
    - mql_id TEXT
    - seller_id TEXT
    - sdr_id TEXT
    - sr_id TEXT
    - won_date TEXT
    - business_segment TEXT
    - lead_type TEXT
    - lead_behaviour_profile TEXT
    - has_company INTEGER
    - has_gtin INTEGER
    - average_stock TEXT
    - business_type TEXT
    - declared_product_catalog_size REAL
    - declared_monthly_revenue REAL


TABLE main.leads_qualified
-------------------------
  COLUMNS:
    - mql_id TEXT
    - first_contact_date TEXT
    - landing_page_id TEXT
    - origin TEXT


TABLE main.order_items
---------------------
  COLUMNS:
    - order_id TEXT
    - order_item_id INTEGER
    - product_id TEXT
    - seller_id TEXT
    - shipping_limit_date TEXT
    - price REAL
    - freight_value REAL


TABLE main.order_payments
------------------------
  COLUMNS:
    - order_id TEXT
    - payment_sequential INTEGER
    - payment_type TEXT
    - payment_installments INTEGER
    - payment_value REAL


TABLE main.order_reviews
-----------------------
  COLUMNS:
    - review_id TEXT
    - order_id TEXT
    - review_score INTEGER
    - review_comment_title TEXT
    - review_comment_message TEXT
    - review_creation_date TEXT
    - review_answer_timestamp TEXT


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


TABLE main.product_category_name_translation
-------------------------------------------
  COLUMNS:
    - product_category_name TEXT
    - product_category_name_english TEXT


TABLE main.products
------------------
  COLUMNS:
    - product_id TEXT
    - product_category_name TEXT
    - product_name_lenght REAL
    - product_description_lenght REAL
    - product_photos_qty REAL
    - product_weight_g REAL
    - product_length_cm REAL
    - product_height_cm REAL
    - product_width_cm REAL


TABLE main.sellers
-----------------
  COLUMNS:
    - seller_id TEXT
    - seller_zip_code_prefix INTEGER
    - seller_city TEXT
    - seller_state TEXT
    """,
    
    temperature=0.8,
    max_output_tokens=1500
)
print(response.output[0].content[0].text)