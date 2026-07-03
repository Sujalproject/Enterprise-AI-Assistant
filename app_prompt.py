from models import model

from pydantic import BaseModel, Field
from typing import Literal

class RouteQuery(BaseModel):
    datasource: Literal["rag", "chat"] = Field(
        description="Route to 'rag' if the answer requires the uploaded documents. Otherwise route to 'chat'."
    )
    
router_llm = model.with_structured_output(RouteQuery)

