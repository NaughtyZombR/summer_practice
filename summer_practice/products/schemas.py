from datetime import datetime
from enum import Enum

from pydantic import BaseModel


# Stores + StoreItems
class StoreItemModelsEnum(str, Enum):
    Product = "Product"
    Book = "Book"
    StoreItem = "StoreItem"


class StoreBase(BaseModel):
    title: str
    url: str
    items_model: StoreItemModelsEnum


class StoreCreate(StoreBase):
    pass


class Store(StoreBase):
    id: int
    total_items: int
    created_at: datetime

    class Config:
        orm_mode = True


# ----

class ProductBase(BaseModel):
    title: str
    price: float
    url: str
    picture: str


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_model = True


# ------

class AliexpressProductBase(ProductBase):
    rating: int | None
    bought: int | None


class AliexpressProductCreate(AliexpressProductBase):
    pass


class AliexpressProduct(AliexpressProductBase, Product):
    class Config:
        orm_mode = True


# ------


class BookBase(ProductBase):
    year_publishing: int
    description: str
    authors: list[str]
    publisher: str
    pages: str
    category: str


class BookCreate(BookBase):
    pass


class Book(Product, BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ------


class BlacklistBase(BaseModel):
    title: str
    url: str


class BlacklistCreate(BlacklistBase):
    product_id: int


class Blacklist(BlacklistBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# RESPONSE
# ------

class ProductMeta(BaseModel):
    store_id: int
    offset: int
    limit: int
    total: int

    class Config:
        orm_mode = True


class ProductResponse(BaseModel):
    data: list[AliexpressProduct | Book]
    meta: ProductMeta

    class Config:
        orm_mode = True


# Single Responses
class SingleProductMeta(BaseModel):
    store_id: int

    class Config:
        orm_mode = True


class SingleProductResponse(BaseModel):
    data: AliexpressProduct | Book
    meta: SingleProductMeta

    class Config:
        orm_mode = True


class SingleStoreResponse(Store):
    items: list[AliexpressProduct | Book]

    class Config:
        orm_mode = True
