from sqlalchemy import Column, Integer, Float, String, ForeignKey
from syurbot_db.db_models.tagset import TagSetModel
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class WordModel(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    word = Column(String(45))
    tagset_id = Column(Integer, ForeignKey(TagSetModel.id))
    frequency = Column(Float)
    word_source = Column(String(15))

    def __repr__(self):
        return "<WordModel(word={}, tagset_id={}, frequency{}, source{})>".format(
            self.id,
            self.word,
            self.tags_id,
            self.frequency,
            self.source
        )
