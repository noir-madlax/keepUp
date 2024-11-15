from pydantic import BaseModel

class ParseRequest(BaseModel):
    id: int
    url: str
    content: str | None = None 