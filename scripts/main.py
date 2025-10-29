# import kagglehub

# # Download latest version
# path = kagglehub.dataset_download("terencicp/e-commerce-dataset-by-olist-as-an-sqlite-database")

# print("Path to dataset files:", path)
from promptbuilder import PromptConstructor
import os
from dotenv import load_dotenv
import openai

load_dotenv()

YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")
YANDEX_CLOUD_MODEL = os.getenv("YANDEX_CLOUD_MODEL")


context = """
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
"""

user_prompt = "Покажи количество клиентов по городам и регионам, где больше 100 клиентов"

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
    temperature=0.8,
    max_output_tokens=1500
)
print("Model Response:\n", response.output[0].content[0].text)