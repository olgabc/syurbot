from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class WordModel(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    word = Column(String(45))
    pos = Column(String(4))
    tags_set_num = Column(Integer)
    tags_info = Column(String(200))
    frequency = Column(Float)
    source = Column(String(15))

    def __repr__(self):
        return "<WordModel(word={}, pos={}, tags_set_num={}, tags_info={}, frequency{}, source{})>".format(
            self.id,
            self.word,
            self.pos,
            self.tags_set_num,
            self.tags_info,
            self.frequency,
            self.source
        )
