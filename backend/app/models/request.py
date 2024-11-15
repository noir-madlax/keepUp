from pydantic import BaseModel

class FetchRequest(BaseModel):
    id: int
    url: str

class ParseRequest(BaseModel):
    id: int
    url: str
    content: str | None = None 