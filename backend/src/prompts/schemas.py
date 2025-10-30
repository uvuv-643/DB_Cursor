from pydantic import BaseModel, Field


class Prompt(BaseModel): 
    prompt:str = Field(..., description="Prompt to be sent to the model")
