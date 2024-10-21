from pydantic import BaseModel

class ItemModel(BaseModel):
    id : str | None
    name : str
    amount : int
    price : int
    cost : float