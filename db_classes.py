from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class FreqDict(Base):
    __tablename__ = "frequency_dict"
    id = Column(Integer, primary_key=True)
    lemma = Column(String)
    dict_pos = Column(String)
    pos = Column(String)
    by_hands_tags = Column(String)
    frequency = Column(Float)

    def __repr__(self):
        return "<FreqDict(lemma={}, dict_pos={}, pos={}, by_hands_tags={}, frequency={})>".format(
            self.lemma,
            self.dict_pos,
            self.pos,
            self.by_hands_tags,
            self.frequency
        )


class WordsDict(Base):
    __tablename__ = "words_dict"
    id = Column(Integer, primary_key=True)
    words_dict_json = Column(String)

    def __repr__(self):
        return "<FreqDict(words_dict={})>".format(self.words_dict_json)
