from sqlalchemy import Column, Integer, ForeignKey
from syurbot_db.tag import TagModel
from syurbot_db.tagset import TagSetModel
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TagSetHasTagModel(Base):
    __tablename__ = "tagset_has_tag"
    id = Column(Integer, primary_key=True)
    tagset_id = Column(Integer, ForeignKey(TagSetModel.id))
    tag_id = Column(Integer, ForeignKey(TagModel.id))

    def __repr__(self):
        return "<TagSetHasTagModel(tagset_id={}. tag_id={})>".format(
            self.tagset_id,
            self.tag_id
        )
