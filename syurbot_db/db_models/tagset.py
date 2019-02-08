from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TagsetModel(Base):
    __tablename__ = "tagset"
    id = Column(Integer, primary_key=True)
    hash = Column(String(32), unique=True)

    def __repr__(self):
        return "<TagsetModel(hash = {}>".format(self.hash)
