import os
import sys
from os.path import join, dirname, realpath
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serializable(self):
        return {
            'name': self.name,
            'id': self.id
        }


class Sport(Base):
    __tablename__ = 'sport'

    name = Column(String(80), nullable=False, unique=True)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    image = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'), default=1)
    category = relationship(Category, backref="sports")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serializable(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': join(dirname(realpath(__file__)),
                          'static/uploads/', self.image)

        }


engine = create_engine('sqlite:///sports.db')
Base.metadata.create_all(engine)
