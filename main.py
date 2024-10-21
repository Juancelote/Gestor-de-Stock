from fastapi import FastAPI, HTTPException
from routers import items_route

app = FastAPI()

app.include_router(items_route.item_route)
