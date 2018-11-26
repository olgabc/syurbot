from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TagSetModel(Base):
    __tablename__ = "tagset"
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<TagSetModel()>"
