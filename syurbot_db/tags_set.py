from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TagsSetModel(Base):
    __tablename__ = "tags_set"
    id = Column(Integer, primary_key=True)
    tags_set = Column(String(200))

    def __repr__(self):
        return "<TagsSetModel(tags_set={})>".format(
            self.tags_set
        )
