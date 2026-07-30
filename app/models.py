from pydantic import BaseModel
from typing import List


class ProductRequest(BaseModel):
    producto: str
    plataformas: List[str]
