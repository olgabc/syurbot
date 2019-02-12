from sqlalchemy import Column, Integer, Float, String, ForeignKey
from syurbot_db.db_models.tagset import TagsetModel
from syurbot_db.db_models.source import SourceModel
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class WordModel(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    word = Column(String(45), nullable=False)
    tagset_id = Column(Integer, ForeignKey(TagsetModel.id), nullable=False)
    source_id = Column(Integer, ForeignKey(SourceModel.id), nullable=False)
    hash = Column(String(32), nullable=False, unique=True)
    frequency = Column(Float, nullable=False)


    def __repr__(self):
        return "<WordModel(word={}, tagset_id={}, source_id{}, hash{}, frequency{})>".format(
            self.id,
            self.word,
            self.tags_id,
            self.source_id,
            self.hash,
            self.frequency,

        )
