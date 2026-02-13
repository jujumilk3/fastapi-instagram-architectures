from pydantic import BaseModel


class HashtagResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
