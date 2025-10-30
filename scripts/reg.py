import re

text = """
Покупатели // SELECT customer_id, customer_unique_id FROM main.customers

Количество проданных продуктов в заказах // SELECT order_id, order_items.product_id FROM main.orders JOIN main.order_items ON main.orders.order_id = main.order_items.order_id

Товары с высотой больше 9 // SELECT product_id, product_height_cm FROM main.products WHERE product_height_cm > 9

Товары с весом больше 1500 // SELECT product_id, product_weight_g FROM main.products WHERE product_weight_g > 1500

Объединённый SQL запрос:
SELECT customer_id, customer_unique_id FROM main.customers
JOIN main.orders ON main.customers.customer_id = main.orders.customer_id
JOIN main.order_items ON main.orders.order_id = main.order_items.order_id
JOIN main.products ON main.order_items.product_id = main.products.product_id
WHERE main.products.product_height_cm > 9 AND main.products.product_weight_g > 1500;
"""

pattern_double_slash = re.compile(
    r'^(?P<title>.+?)\s*//\s*(?P<sql>SELECT\b[\s\S]*?)(?=\n{2,}|$)',
    re.IGNORECASE | re.MULTILINE
)


answer = { txt: {
        "table": re.findall(r'(?i)\b(?:from|join|update|into)\b\s+([a-z_][\w.]*)', sql_code),
        "columns": re.findall(r'(?i)\bselect\b\s+(.*?)\s+\bfrom\b', sql_code),
        "where": re.findall(r'(?is)\bwhere\b\s+(.+?)(?=(?:\bgroup\b|\border\b|;|$))', sql_code)
    } for txt, sql_code in re.findall(pattern_double_slash, text)}

print(answer)