from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Foo",
                "description": "The pretender",
                "price": 42.0,
                "tax": 3.2
            }
        }
    }


@app.put("/items/{item_id}", tags=['items'], summary="AAA", response_model=Item,
         status_code=status.HTTP_200_OK, deprecated=False)
async def update_item(item_id: int, item: Item):
    """
    dadaddudududududu
    - as
    - sda
    - sdg
    """
    results = {"item_id": item_id, "item": item}
    return results


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000)
