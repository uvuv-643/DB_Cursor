from pydantic import BaseModel


class Credentials(BaseModel): 
    driver:str
    host:str
    port:str
    database:str
    username:str
    password:str
