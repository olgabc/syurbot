from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TagsetModel(Base):
    __tablename__ = "tagset"
    id = Column(Integer, primary_key=True, )

    def __repr__(self):
        return "<TagsetModel()>"
