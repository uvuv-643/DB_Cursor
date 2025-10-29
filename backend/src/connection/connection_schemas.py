from pydantic import BaseModel

class Creditians(BaseModel): 
    driver:str
    host:str
    port:str
    database:str
    username:str
    password:str


