from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from summer_practice.products import crud, schemas, models, utils
from ..crud import get_all_objects, create_object, update_object, delete_object
from summer_practice.database import get_db

# region STORES
# ----

router_stores = APIRouter(prefix="/stores", tags=["stores"])


@router_stores.post("/create/", response_model=schemas.Store)
async def create_store(store_data: schemas.StoreCreate, db: Session = Depends(get_db)):
    new_store = models.Store(**store_data.dict())
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store


@router_stores.get("/show/", response_model=list[schemas.Store])
async def read_stores(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stores = get_all_objects(db=db, model=models.Store, offset=offset, limit=limit)
    return stores


@router_stores.get("/show/{store_id}/", response_model=schemas.SingleStoreResponse)
async def get_store(store_id: int, limit_items: int = 20, db: Session = Depends(get_db)):
    store = crud.get_object_by_id(db=db, model=models.Store, obj_id=store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")

    limit_items = min(max(limit_items, 1), 50)  # Ограничение в минимум 1 и максимум 50 товаров в информации о магазине

    store_dict = schemas.Store.from_orm(store).dict()  # Преобразуем объект store в словарь

    store_dict["items"] = store.items[:limit_items]  # Заменяем поле items

    limited_store = schemas.SingleStoreResponse(**store_dict)  # Создаем новый объект с модифицированными данными

    return limited_store


@router_stores.put("/update/{store_id}", response_model=schemas.Store)
async def update_store(store_id: int, store: schemas.StoreBase, db: Session = Depends(get_db)):
    db_store = crud.get_object_by_id(db, model=models.Store, obj_id=store_id)

    if db_store is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Store not found.")

    db_product = update_object(db=db, model=db_store, schema=store)
    return db_product


@router_stores.delete("/delete/{store_id}")
async def delete_store(store_id: int, db: Session = Depends(get_db)):
    db_store = crud.get_object_by_id(db, model=models.Store, obj_id=store_id)
    if db_store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Store not found.")

    delete_object(db, db_store)
    return Response(status_code=status.HTTP_200_OK,
                    content=f"Запись (ID: {store_id}) таблицы '{db_store.__tablename__}' была удалена.")

# endregion STORES

# region PRODUCTS

router_products = APIRouter(prefix="/products", tags=["products"])


@router_products.post("/create/", description="**ТУТ ИСПОЛЬЗУЕТСЯ ДВЕ РАЗНЫХ СХЕМЫ ДЛЯ СОЗДАНИЯ STORE_ITEM**",
                      response_model=schemas.SingleProductResponse)
async def create_store_item(store_id: int,
                            item_data: schemas.BookCreate | schemas.AliexpressProductCreate,
                            db: Session = Depends(get_db)):
    if crud.is_product_in_blacklist(db, item_data):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="This product is blacklisted.")

    store = db.query(models.Store).get(store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")

    item_class = store.items_model
    item_model = getattr(models, item_class)  # Получаем класс модели из модуля

    db_product = crud.get_product_by_url(db, model=item_model, product_url=item_data.url, store=store)
    if db_product:
        # нарушение уникального ограничения, вернуть HTTPException 409 Conflict
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item with this URL already exists")

    try:
        new_item = create_object(db=db, model=item_model, schema=item_data, store=store)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The passed item is not valid for this Store")

    # if isinstance(item_data, schemas.BookCreate):
    #     Обработка схемы BookCreate
        # return {"message": "Book created"}
    # elif isinstance(item_data, schemas.AliexpressProductCreate):
    #     Обработка  схемы AliexpressProductCreate
        # return {"message": "Aliexpress product created"}
    meta = schemas.SingleProductMeta(store_id=store_id)
    response = schemas.SingleProductResponse(data=new_item, meta=meta)
    return response


@router_products.get("/show/", response_model=schemas.ProductResponse)
async def read_store_items(store_id: int, offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    item_model = utils.get_store_item_model(db=db, store_id=store_id)

    products = crud.get_all_objects(db=db, model=item_model, offset=offset, limit=limit, store_id=store_id)

    meta = schemas.ProductMeta(store_id=store_id, offset=offset, limit=limit,
                               total=len(crud.get_all_objects(db=db, model=item_model)))

    response = schemas.ProductResponse(data=products, meta=meta)

    return response


@router_products.delete("/delete_all/")
async def delete_products(store_id: int, db: Session = Depends(get_db)):
    item_model = utils.get_store_item_model(db=db, store_id=store_id)

    products = crud.get_all_objects(db=db, model=item_model, store_id=store_id)

    for product in products:
        delete_object(db, product)

    return Response(status_code=status.HTTP_200_OK,
                    content=f"Таблица '{item_model.__class__.__name__}' была очищена.")


# Можно было бы использовать response_model_exclude_unset=True, вместо создания отдельной схемы SingleProductMeta,
# Но мне показалось, что так поступить правильней.
@router_products.get("/show/{product_id}", response_model=schemas.SingleProductResponse)
async def read_product(store_id: int, product_id: int, db: Session = Depends(get_db)):
    item_model = utils.get_store_item_model(db=db, store_id=store_id)

    db_product = crud.get_product(db, model=item_model, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Item not found.")

    meta = schemas.SingleProductMeta(store_id=store_id)
    response = schemas.SingleProductResponse(data=db_product, meta=meta)

    return response


@router_products.put("/update/{product_id}", response_model=schemas.SingleProductResponse)
async def update_product(store_id: int,
                         product_id: int,
                         item_data: schemas.AliexpressProductCreate | schemas.BookCreate,
                         db: Session = Depends(get_db)):
    item_model = utils.get_store_item_model(db=db, store_id=store_id)

    db_product = crud.get_product(db, model=item_model, product_id=product_id)

    if db_product is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Item not found.")

    try:
        db_product = update_object(db=db, model=db_product, schema=item_data)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The passed item is not valid for this Store")

    meta = schemas.SingleProductMeta(store_id=store_id)
    response = schemas.SingleProductResponse(data=db_product, meta=meta)

    return response


@router_products.delete("/delete/{product_id}")
async def delete_product(store_id: int, product_id: int, db: Session = Depends(get_db)):
    item_model = utils.get_store_item_model(db=db, store_id=store_id)

    db_product = crud.get_product(db, model=item_model, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Item not found.")

    delete_object(db, db_product)
    return Response(status_code=status.HTTP_200_OK,
                    content=f"Запись (ID: {product_id}) таблицы '{item_model.__tablename__}' была удалена.")


# endregion PRODUCTS

# region BLACKLIST
# ----

router_blacklist = APIRouter(prefix="/blacklist", tags=["blacklist"])


@router_blacklist.get("/show/")
async def read_blacklist(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    blacklist = crud.get_blacklist(db, offset=offset, limit=limit)
    return blacklist


@router_blacklist.post("/create_entry/",
                       description="# **При внесении продукта в черный список, он будет автоматически удалён**")
async def create_blacklist_entry(store_id: int, product_id: int, db: Session = Depends(get_db)):
    item_model = utils.get_store_item_model(db=db, store_id=store_id)
    db_product = crud.get_product(db, model=item_model, product_id=product_id)

    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Item not found.")

    db_blacklist = crud.get_blacklist_entry_by_url(db, db_product.url)

    if db_blacklist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This item already in blacklist.")

    return crud.create_blacklist_entry(db=db, product=db_product)


@router_blacklist.get("/show_entry/{blacklist_entry_id}", response_model=schemas.Blacklist)
async def read_blacklist_entry(blacklist_entry_id: int, db: Session = Depends(get_db)):
    db_blacklist_entry = crud.get_blacklist_entry_by_id(db, blacklist_entry_id=blacklist_entry_id)
    if db_blacklist_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="The entry in blacklist not found.")
    return db_blacklist_entry


@router_blacklist.put("/update_entry/{blacklist_entry_id}", response_model=schemas.Blacklist)
async def update_blacklist_entry(blacklist_entry_id: int,
                                 blacklist_entry: schemas.BlacklistBase, db: Session = Depends(get_db)):
    db_blacklist_entry = crud.get_blacklist_entry_by_id(db, blacklist_entry_id=blacklist_entry_id)

    if db_blacklist_entry is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The entry in blacklist not found.")

    db_product = crud.update_blacklist_entry(db, db_blacklist_entry, blacklist_entry)
    return db_product


@router_blacklist.delete("/delete_entry/{blacklist_entry_id}")
async def delete_blacklist_entry(blacklist_entry_id: int, db: Session = Depends(get_db)):
    db_blacklist_entry = crud.get_blacklist_entry_by_id(db, blacklist_entry_id=blacklist_entry_id)

    if db_blacklist_entry is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The entry in blacklist not found.")

    crud.delete_blacklist_entry(db, db_blacklist_entry)
    return Response(status_code=status.HTTP_200_OK,
                    content=f"Запись (ID: {blacklist_entry_id}) удалена из чёрного списка.")
# endregion BLACKLIST
