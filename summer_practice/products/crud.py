from sqlalchemy.orm import Session

from summer_practice.crud import filter_objects, get_object_by_id, get_all_objects, create_object
from summer_practice.database import Base
from summer_practice.products import models
from summer_practice.products import schemas
from summer_practice.products.schemas import BlacklistBase


def get_products(db: Session, model: Base, offset: int = 0, limit: int = 100):
    return get_all_objects(db=db, model=model, offset=offset, limit=limit)


def get_product(db: Session, model: Base, product_id: int):
    return get_object_by_id(db=db, model=model, obj_id=product_id)


def get_product_by_url(db: Session, model: Base, product_url: str, store: models.Store):
    return filter_objects(db=db, model=model, url=product_url, store=store).first()


def is_product_in_blacklist(db: Session, product: schemas.ProductBase) -> bool:
    if get_blacklist_entry_by_url(db, product.url):
        return True
    return False


# ----------


def get_blacklist(db: Session, offset: int = 0, limit: int = 100):
    return get_all_objects(db=db, model=models.Blacklist, offset=offset, limit=limit)


def get_blacklist_entry_by_id(db: Session, blacklist_entry_id: int):
    return get_object_by_id(db=db, model=models.Blacklist, obj_id=blacklist_entry_id)


def get_blacklist_entry_by_url(db: Session, product_url: str):
    return filter_objects(db=db, model=models.Blacklist, url=product_url).first()


def create_blacklist_entry(db: Session, product: models.Product):
    blacklist_entry_data = BlacklistBase(title=product.title, url=product.url)
    db_blacklist_entry = create_object(db=db, model=models.Blacklist, schema=blacklist_entry_data)

    db.delete(product)
    db.commit()

    return db_blacklist_entry


def update_blacklist_entry(db: Session,
                           db_blacklist_entry: models.Blacklist, blacklist_entry: schemas.BlacklistBase):
    # Update model class variable from requested fields
    for var, value in vars(blacklist_entry).items():
        setattr(db_blacklist_entry, var, value) if value or str(value) == 'False' else None

    db.commit()
    db.refresh(db_blacklist_entry)
    return db_blacklist_entry


def delete_blacklist_entry(db: Session, db_blacklist_entry: models.Blacklist):
    db.delete(db_blacklist_entry)
    db.commit()

    return True
