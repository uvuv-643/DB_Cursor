from fastapi import APIRouter, HTTPException, Request, Response
import jwt
import openai
import json
from ..clients.redis_client import redis_client as redis
from ..prompts.context_builder import ContextConstructor
from ..prompts.prompt_builder import PromptConstructor
from ..prompts.schemas import Prompt
from ..settings import (
    SECRET_KEY,
    YANDEX_CLOUD_API_KEY,
    YANDEX_CLOUD_FOLDER,
    YANDEX_CLOUD_MODEL,
)



router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/")
async def run_prompt(promt: Prompt, response: Response, request: Request):
    token_id = request.cookies.get('db_token_id')
    if not token_id:
        raise HTTPException(status_code=401, detail="Token cookie not found")

    key = f"dbtoken:{token_id}"
    token_db = await redis.get(key)
    if not token_db:
        raise HTTPException(status_code=403, detail="Token not found in Redis")

    payload_data = jwt.decode(token_db, SECRET_KEY, algorithms=["HS256"])
    db_url = payload_data["db_url"]

    context_constructor = ContextConstructor(db_backend="postgres", postgres_config=db_url)
    # context_constructor = ContextConstructor(db_backend="sqlite", sqlite_path="./db.sqlite")

    context = context_constructor.build()

    prompt_constructor = PromptConstructor(
        yandex_cloud_folder=YANDEX_CLOUD_FOLDER,
        yandex_cloud_model=YANDEX_CLOUD_MODEL
    )
    prompt = prompt_constructor.build_prompt(promt.prompt, context)

    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project= YANDEX_CLOUD_FOLDER
    )

    response = client.responses.create(
        model=f"gpt://{prompt_constructor.folder}/{prompt_constructor.model}",
        input=prompt,
        temperature=0.8,
        max_output_tokens=1500
    )
    json_response = response.output[0].content[0].text
    json_response = json_response.replace("```",'')
    print(json_response)
    data = json.loads(json_response)
    return data
