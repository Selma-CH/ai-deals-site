from pydantic import BaseModel
from typing import List

class Article(BaseModel):
    id: int
    title: str
    content: str
    images: List[str]
    source_url: str
    affiliate_link: str