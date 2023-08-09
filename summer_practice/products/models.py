from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, DateTime, func, JSON, ForeignKey
from sqlalchemy.orm import relationship, declared_attr, validates

from summer_practice.database import Base


class StoreItem(Base):
    __tablename__ = "store_items"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Float)
    url = Column(String, unique=True)
    picture = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.now, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=func.now())

    @declared_attr
    def store_id(self):
        return Column(Integer, ForeignKey('stores.id'))

    @validates('store_id')
    def validate_store_id(self, key, store_id):
        if not self.store or self.store.id != store_id:
            raise ValueError("Invalid store_id")
        return store_id

    store = relationship("Store", back_populates="items", foreign_keys="[StoreItem.store_id]")


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    items_model = Column(String)
    url = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("StoreItem", back_populates="store")

    @property
    def total_items(self):
        return len(self.items)


class Product(StoreItem):
    __tablename__ = "products"

    id = Column(Integer, ForeignKey("store_items.id"), primary_key=True)
    rating = Column(Integer, nullable=True)
    bought = Column(Integer, nullable=True)


class Book(StoreItem):
    __tablename__ = "books"

    id = Column(Integer, ForeignKey("store_items.id"), primary_key=True)
    year_publishing = Column(Integer)
    description = Column(String)
    authors = Column(JSON)
    publisher = Column(String)
    pages = Column(String)
    category = Column(String)


class Blacklist(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
