from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()


class TagSetHasTagModel(Base):
    __tablename__ = "tagset_has_tag"
    id = Column(Integer, primary_key=True)
    children = relationship("tagset", "tag")
    tagset_id = Column(Integer)
    tag_id = Column(Integer)

    def __repr__(self):
        return "<TagSetHasTagModel(tagset_id={}. tag_id={})>".format(
            self.tagset_id,
            self.tag_id
        )
