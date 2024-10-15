from typing import Annotated, Any, Literal
from enum import Enum

from fastapi import FastAPI, Query, Path, Body, Cookie, Header, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, HttpUrl


class Cookies(BaseModel):
  session_id: str | None = None
  fatebook_tracker: str | None = None
  googall_tracker: str | None = None

class CommonHeaders(BaseModel):
  accept: str | None = None
  host: str | None = None
  save_data: bool | None = None
  if_modified_since: str | None = None
  traceparent: str | None = None
  x_tag: list[str] = []

class ModelName(str, Enum):
  alexnet = "alexnet"
  resnet = "resnet"
  lenet = "lenet"

class Image(BaseModel):
  url: HttpUrl
  name: str

class Item(BaseModel):
  name: str
  description: str | None = Field(default=None, title="The description of the item", max_length=300)
  price: float = Field(gt=0, description="The price must be greater than zero")
  tax: float | None = None
  tags: set[str] = set()
  images: list[Image] | None = None

  model_config = {
    "json_schema_extra": {
      "examples": [
        {
          "name": "Foo",
          "description": "A very nice Item",
          "price": 35.4,
          "tax": 3.2,
        }
      ]
    }
  }

class Offer(BaseModel):
  name: str
  description: str | None = Field(default=None, title="The description of the offer", max_length=300)
  price: float = Field(gt=0, description="The price must be greater than zero")
  items: list[Item]

class BaseUser(BaseModel):
  username: str
  full_name: str | None = None

class UserIn(BaseUser):
  password: str

class FilterParams(BaseModel):
  model_config = {
    "json_schema_extra": {
      "examples": [
        {
          "limit": 10,
          "offset": 5,
          "order_by": "created_at",
          "tags": ["tag1", "tag2"],
        }
      ]
    },
    "extra": "forbid"
  }

  limit: int = Field(100, gt=0, le=100)
  offset: int = Field(0, ge=0)
  order_by: Literal["created_at", "updated_at"] = "created_at"
  tags: list[str] = []

app = FastAPI()

fake_items_db = [{"name": "item 1", "price": 1.99}, {"name": "item 2", "price": 2.99}, {"name": "item 3", "price": 3.99}]


@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/files/{file_type}/{file_path:path}")
async def read_file(file_type: int, file_path: str, test: str | None = None):
  return {"file_type": file_type, "file_path": file_path, "test": test}

@app.get("/items/", response_model=list[Item | dict])
async def read_items(filter_query: Annotated[FilterParams, Query()], ads_id: Annotated[Cookies, Cookie()], headers: Annotated[CommonHeaders, Header()]) -> Any:
  results = [
    {"name": "Portal Gun", "price": 42.0},
    {"name": "Plumbus", "price": 32.0}
  ]
  if filter_query:
    results.append({"filter_query": filter_query.model_dump_json()})
  if ads_id:
    results.append({"ads_id": ads_id.model_dump_json()})
  if headers:
    results.append({"headers": headers.model_dump_json()})
  return results

@app.get("/items/{item_id}", response_model=Item, response_model_include={"tax"})
async def read_item(item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=2)]):
  return fake_items_db[item_id]

@app.get("/portal/", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
  if teleport:
    return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
  return {"message": "Here's your interdimensional portal."}

@app.get("/users/me")
async def read_user_me():
  return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
  return {"user_id": user_id}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
  if model_name is ModelName.alexnet:
    return {"model_name": model_name, "message": "Deep Learning FTW!"}
  
  if model_name is ModelName.lenet:
    return {"model_name": model_name, "message": "LeCNN all the images"}
  
  return {"model_name": model_name, "message": "Have some residuals"}

@app.post("/index-weights")
async def create_index_weights(weights: dict[int, float]):
  return weights

@app.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
  return item

@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

@app.post("user/")
async def create_user(user: UserIn) -> BaseUser:
  return user
    
@app.put("/items/{item_id}")
async def update_item(
  item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
  importance: Annotated[int, Body(ge=1, le=10)],
  item: Item | None = None,
  user: BaseUser | None = None,
):
  results = {"item_id": item_id, **item.model_dump(), **user.model_dump(), "importance": importance}
  return results