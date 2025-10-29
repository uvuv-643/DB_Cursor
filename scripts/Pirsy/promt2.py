import openai

YANDEX_CLOUD_MODEL = ""
YANDEX_CLOUD_FOLDER = ""
YANDEX_CLOUD_API_KEY = ""

user_promt = "покупатели и количество проданных продуктов в заказах с товарами с высотой больше 9 и весом больше 1500"
sql_code = """
SELECT customer_id, COUNT(order_item_id) AS count_of_items
FROM main.orders
JOIN main.order_items USING (order_id)
JOIN main.products USING (product_id)
WHERE product_height_cm > 9 AND product_weight_g > 1500
GROUP BY customer_id;
"""


client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project= YANDEX_CLOUD_FOLDER
)

response = client.responses.create(
    model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
    input=
    f"""Сопоставь фрагменты запроса пользователя с фрагментами SQL запроса:
    =======
    Запрос пользователя:
    {user_promt}. 
    =======
    SQL:
    {sql_code}
    ======
    Приведи ответ в формате
    <цитата #1 из запроса пользовотеля> - <фрагмент #1 sql кода>
    <цитата #2 из запроса пользовотеля> - <фрагмент #1 sql кода>
    ..."""

,
    
    temperature=0.8,
    max_output_tokens=1500
)
print(response.output[0].content[0].text)