import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, \
                       String, TIMESTAMP, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Class to store user information.
    Attributes:
        id: unique id for a user
        name: username
        email: email
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return serialized User object."""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email
        }


class Category(Base):
    """Class to store category information.
    Attributes:
        id: unique id for a category
        name: name of the category
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return serialized Category object."""
        return {
            'name': self.name,
            'id': self.id
        }


class Item(Base):
    """Class to store item information.
    Attributes:
        id: unique id for an item
        name: name of the item
        description: details about item
        created_date: item creation date
        updated_date: item updated date
    """
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    created_date = Column(TIMESTAMP, nullable=False)
    updated_date = Column(TIMESTAMP)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        """Return serialized Item object."""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'created_date': self.created_date,
            'updated_date': self.updated_date
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
