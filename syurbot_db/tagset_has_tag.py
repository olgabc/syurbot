from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TagSetHasTagModel(Base):
    __tablename__ = "tagset_has_tag"
    id = Column(Integer, primary_key=True)
    tagset_id = Column(Integer, ForeignKey("TagSetModel.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("TagModel.id"), nullable=False)

    def __repr__(self):
        return "<TagSetHasTagModel(tagset_id={}. tag_id={})>".format(
            self.tagset_id,
            self.tag_id
        )

