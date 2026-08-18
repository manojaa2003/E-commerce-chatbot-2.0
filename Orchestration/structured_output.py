from pydantic import BaseModel, Field
from typing import Literal

class router_output(BaseModel):
    """user Intent classifier"""

    user_intent: Literal["faq", "sql", "general_qa","fall_back"] = Field(description="user intent")
    