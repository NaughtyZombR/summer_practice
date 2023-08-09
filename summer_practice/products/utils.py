from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from summer_practice.products import models


def get_store_item_model(db: Session, store_id: int) -> models.Base:
    if not store_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Query param 'store_id' was not passed.")
    store = db.query(models.Store).get(store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")

    items_class = store.items_model  # Например, "Product" или "Book"
    item_model = getattr(models, items_class)  # Получаем класс модели из модуля
    return item_model
