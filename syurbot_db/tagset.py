from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TagSetModel(Base):
    __tablename__ = "tagset"
    id = Column(Integer, ForeignKey("tagset_has_tag.tagset"), primary_key=True, )

    def __repr__(self):
        return "<TagSetModel()>"
