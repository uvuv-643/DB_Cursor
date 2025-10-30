import os
import openai

from dotenv import load_dotenv

from contextbuilder import ContextConstructor
from promptbuilder import PromptConstructor

load_dotenv()

YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")
YANDEX_CLOUD_MODEL = os.getenv("YANDEX_CLOUD_MODEL")

builder = ContextConstructor(db_backend="sqlite", sqlite_path="./db.sqlite")
context = builder.build()

# user_prompt = "Покажи количество клиентов которые живут в городах, и zip коды которых начинаются на 12 и 13"
user_prompt = "Определи клиентов с большим кол-вом заказов."

constructor = PromptConstructor(
    yandex_cloud_folder=YANDEX_CLOUD_FOLDER,
    yandex_cloud_model=YANDEX_CLOUD_MODEL
)

prompt = constructor.build_prompt(user_prompt, context)

client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project= YANDEX_CLOUD_FOLDER
)

response = client.responses.create(
    model=f"gpt://{constructor.folder}/{constructor.model}",
    input=prompt,
    temperature=0.5,
    max_output_tokens=1500
)
print("Model Response:\n", response.output[0].content[0].text)