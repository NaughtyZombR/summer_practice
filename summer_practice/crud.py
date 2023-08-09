from pydantic import BaseModel as BaseSchema
from sqlalchemy.orm import Session

from summer_practice.database import Base


def get_object(db: Session, model: Base, **kwargs):
    return filter_objects(db=db, model=model, **kwargs).first()


def get_object_by_id(db: Session, model: Base, obj_id: int):
    return filter_objects(db=db, model=model, id=obj_id).first()


def get_all_objects(db: Session, model: Base, offset: int = 0, limit: int = None, **kwargs):

    if kwargs:
        query = filter_objects(db=db, model=model, **kwargs).offset(offset)
    else:
        query = db.query(model).offset(offset)

    if limit is not None:
        query = query.limit(limit)
    return query.all()


def filter_objects(db: Session, model: Base, **kwargs):
    # Проверяем, что переданные атрибуты существуют в модели
    valid_attributes = [attr for attr in kwargs.keys() if hasattr(model, attr)]
    # Строим фильтр, используя только существующие атрибуты
    filters = [getattr(model, attr) == value for attr, value in kwargs.items() if attr in valid_attributes]
    # Возвращаем Query объект для возможности дальнейшего модифицирования запроса
    return db.query(model).filter(*filters)


def create_object(db: Session, model: Base, schema: BaseSchema, **kwargs):
    obj_data = schema.dict()
    obj_data.update(kwargs)
    obj = model(**obj_data)

    db.add(obj)
    db.commit()
    db.refresh(obj)  # Обновляем объект, чтобы получить автоматически сгенерированные значения, если таковые есть

    return obj


def delete_all_objects(db: Session, model: Base):
    db.query(model).delete()
    db.commit()
    return


def update_object(db: Session, model: Base, schema: BaseSchema):
    for var, value in vars(schema).items():
        setattr(model, var, value) if value or str(value) == 'False' else None

    db.commit()
    db.refresh(model)
    return model


def delete_object(db: Session, model: Base):
    db.delete(model)
    db.commit()
    return
