# Este esquema transforma lo recibido de MongoDB, a lo que espera recibir el FastAPI, solo aplica uno a la vez.
def item_schema(item) -> dict:
    return {"id": str(item["_id"]),
            "name": item["name"],
            "amount": item["amount"],
            "price": item["price"],
            "cost": item["cost"],}

# Este esquema, toma retorna varios esquemas a la vez en un array.
def items_schema(items) -> list:
    return [item_schema(item) for item in items]