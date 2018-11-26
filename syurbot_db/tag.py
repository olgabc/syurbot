from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TagModel(Base):
    """
    :param __table__:
    """
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    tag = Column(String(10))

    def __repr__(self):
        return "<TagModel(tag={})>".format(self.tag)