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
            f"""Раздели данный запрос на несколько связанных по смыслу фрагментов: {user_prompt}. 
В ответе перечисляй только фрагменты из текста, разделённые "//". 
После каждого фрагмента в скобках реализуй SQL-запрос для этого фрагмента 
(все фрагменты должны быть частью одного SQL-запроса). 
В конце объедини все SQL-фрагменты.

Формат ответа: JSON с ключами:
- "partial_queries": dict[str, str] — SQL-запросы по каждому фрагменту
- "full_query": str — итоговый объединённый SQL-запрос

{context}
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
