from sqlalchemy import Column, Integer, Float, String, ForeignKey
from syurbot_db.db_models.tagset import TagSetModel
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class WordModel(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    word = Column(String(45))
    pos = Column(String(4))
    tagset_id = Column(Integer, ForeignKey(TagSetModel.id))
    frequency = Column(Float)
    word_source = Column(String(15))

    def __repr__(self):
        return "<WordModel(word={}, pos={}, tagset_id={}, tags={}, frequency{}, source{})>".format(
            self.id,
            self.word,
            self.pos,
            self.tags_set_num,
            self.tags_info,
            self.frequency,
            self.source
        )
