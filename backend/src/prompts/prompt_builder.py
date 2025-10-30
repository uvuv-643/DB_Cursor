class PromptConstructor:
    def __init__(self, yandex_cloud_folder: str, yandex_cloud_model: str):
        """
        :param yandex_cloud_folder: Идентификатор папки Yandex Cloud.
        :param yandex_cloud_model: Имя модели Yandex Cloud.
        """
        self.folder = yandex_cloud_folder
        self.model = yandex_cloud_model

    def build_prompt(self, user_prompt: str, context: str) -> str:
        """
        Собирает текст промпта, передаваемого в модель.

        :param user_prompt: Запрос пользователя, который нужно разбить и преобразовать.
        :param context: Описание структуры БД или другой контекст.
        :return: Готовый текст промпта.
        """
        prompt = (
            f"""Ты - эксперт по SQL и обработке естественного языка. Твоя задача - преобразовать пользовательский запрос на естественном языке в структурированный словарь с SQL-запросами.

ПРАВИЛА:
1. Анализируй структуру базы данных из контекста: {context}
2. Разбивай пользовательский запрос: {user_prompt} на части ДОБУКВЕННО совпадающие с исходным текстом
3. Формируй dict где ключи - точные подстроки из запроса, значения - соответствующие SQL-фрагменты
4. Если запрос некорректен или не соответствует структуре БД - возвращай пустой dict {{}}

СТРУКТУРА ОТВЕТА:
{{
  "часть запроса 1": "SQL фрагмент 1",
  "часть запроса 2": "SQL фрагмент 2"
}}

БАЗА ДАННЫХ:
{context}

ПРИМЕРЫ:

Запрос: "товары где цена больше 1000 и название содержит 'apple'"
База: таблицы products(id, name, price), categories(id, category_name)
Ответ:
{{
  "товары": "SELECT * FROM products",
  "цена больше 1000": "WHERE price > 1000", 
  "название содержит 'apple'": "AND name LIKE '%apple%'"
}}

Запрос: "клиенты из Москвы с заказами дороже 5000"
База: таблицы customers(id, name, city), orders(id, customer_id, amount)
Ответ:
{{
  "клиенты": "SELECT customers.* FROM customers",
  "из Москвы": "WHERE customers.city = 'Москва'",
  "с заказами": "JOIN orders ON customers.id = orders.customer_id",
  "дороже 5000": "AND orders.amount > 5000"
}}

Запрос: "пользователи у которых email заканчивается на gmail.com и дата регистрации после 2023 года"
База: таблицы users(user_id, email, reg_date), profiles(user_id, full_name)
Ответ:
{{
  "пользователи": "SELECT * FROM users",
  "email заканчивается на gmail.com": "WHERE email LIKE '%gmail.com'",
  "дата регистрации после 2023 года": "AND reg_date > '2023-01-01'"
}}

Запрос: "заказы с товарами из категории электроника"
База: таблицы orders(id, product_id), products(id, name, category_id), categories(id, name)
Ответ:
{{
  "заказы": "SELECT orders.* FROM orders",
  "с товарами": "JOIN products ON orders.product_id = products.id", 
  "из категории электроника": "JOIN categories ON products.category_id = categories.id WHERE categories.name = 'электроника'"
}}

Запрос: "некорректный бредовый запрос"
Ответ: {{}}

АЛГОРИТМ:
1. Идентифицируй основную сущность (таблицу) из запроса
2. Найди все условия фильтрации в запросе
3. Сопоставь условия с полями базы данных
4. Разбей запрос на точные подстроки
5. Сформируй SQL фрагменты для каждой подстроки

Теперь обработай запрос: {user_prompt}
"""
        )
        return prompt

    def build_request(self, user_prompt: str, context: str, temperature: float = 0.8, max_tokens: int = 1500) -> str:
        """
        Формирует готовый код запроса к модели.

        :param user_prompt: Запрос пользователя.
        :param context: Контекст (описание таблиц и схем).
        :param temperature: Параметр случайности модели.
        :param max_tokens: Максимальное количество токенов в ответе.
        :return: Строка с кодом Python-запроса.
        """
        prompt = self.build_prompt(user_prompt, context)

        request_code = f"""response = client.responses.create(
                model=f"gpt://{{self.folder}}/{{self.model}}",
                input=f"{prompt}",
                temperature={temperature},
                max_output_tokens={max_tokens}
            )"""
        return request_code
