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
            f"""
Ты - эксперт по SQL и обработке естественного языка. Твоя задача - преобразовать пользовательский запрос на естественном языке в структурированный JSON с двумя частями.

КОНТЕКСТ БАЗЫ ДАННЫХ:
{context}

ИНСТРУКЦИИ ДЛЯ FIRST_PART:
1. Разбей пользовательский запрос на логические части ДОБУКВЕННО совпадающие с исходным текстом
2. Для каждой части создай соответствующий SQL фрагмент на основе схемы базы данных
3. Ключи должны точно соответствовать подстрокам из исходного промпта
4. SQL должен быть корректным для данной базы данных
5. Если запрос некорректен или не соответствует схеме - верни пустой dict

ИНСТРУКЦИИ ДЛЯ SECOND_PART:
1. Создай массив из 3 SQL запросов с нарастающей строгостью
2. Каждый следующий запрос должен возвращать ПОДМНОЖЕСТВО данных предыдущего
3. Запросы должны быть корректными для схемы базы данных
4. Используй WHERE, JOIN, дополнительные условия для создания "воронки"
5. Возвращай COUNT а не просто *.

ФОРМАТ ОТВЕТА - строго валидный JSON:
{{
  "first_part": {{
    "текст часть 1": "SQL фрагмент 1",
    "текст часть 2": "SQL фрагмент 2"
  }},
  "second_part": [
    "SELECT запрос 1 (самый широкий)",
    "SELECT запрос 2 (строже)", 
    "SELECT запрос 3 (самый строгий)"
  ]
}}

ПРИМЕРЫ:

Пример 2:
Пользователь: "заказы созданные после 2023 года со статусом 'доставлен' где клиент из города 'Москва'"

Ответ:
{{
  "first_part": {{
    "заказы": "SELECT * FROM orders",
    "созданные после 2023 года": "WHERE created_at > '2023-01-01'",
    "со статусом 'доставлен'": "AND status = 'delivered'", 
    "клиент из города 'Москва'": "JOIN customers ON orders.customer_id = customers.id WHERE customers.city = 'Москва'"
  }},
  "second_part": [
    "SELECT COUNT(*) FROM orders WHERE created_at > '2023-01-01'",
    "SELECT COUNT(*) FROM orders WHERE created_at > '2023-01-01' AND status = 'delivered'",
    "SELECT COUNT(*) FROM orders JOIN customers ON orders.customer_id = customers.id WHERE created_at > '2023-01-01' AND status = 'delivered' AND customers.city = 'Москва'"
  ]
}}

Пример 3 (с JOIN и переводом):
Пользователь: "товары у которых перевод категории на английский 'home_appliances'"

Ответ:
{{
  "first_part": {{
    "товары": "SELECT * FROM products",
    "перевод категории на английский 'home_appliances'": "JOIN category_translation ON products.category_id = category_translation.category_id WHERE category_translation.category_name_english = 'home_appliances'"
  }},
  "second_part": [
    "SELECT COUNT(*) FROM products JOIN category_translation ON products.category_id = category_translation.category_id WHERE category_translation.category_name_english = 'home_appliances'"
  ]
}}

ВАЖНЫЕ ПРАВИЛА:
1. Ключи в first_part ДОЛЖНЫ точно совпадать с подстроками из пользовательского промпта
2. Все SQL выражения должны быть корректны для схемы базы данных
3. В second_part каждый следующий запрос должен быть СТРОЖЕ предыдущего
4. Используй JOIN только когда необходимо по смыслу запроса
5. Если запрос невозможно корректно обработать - верни {{"first_part": {{}}, "second_part": []}}

ПОЛЬЗОВАТЕЛЬСКИЙ ЗАПРОС: {user_prompt}
ОЧЕНЬ ВАЖНО: ДЕЛАЙ ВСЕ РОВНО ИЗ ТОГО ЧТО ЕСТЬ В СХЕМЕ БД. ЕСЛИ КОЛОНОК НЕТ В БД - НЕ ПИШИ ИХ. КОНТЕКСТ БД ПРИЛАГАЕТСЯ.
Кроме того для второй части делай ОЧЕНЬ атомарные предложения. То есть их должно быть как можно больше и во второй части они НЕ ДОЛЖНЫ ПОВТОРЯТЬСЯ!!!

Сгенерируй ответ строго в указанном JSON формате:
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
