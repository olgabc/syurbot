from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class FrequencyModel(Base):
    __tablename__ = "frequency"
    id = Column(Integer, primary_key=True)
    lemma = Column(String)
    dict_pos = Column(String)
    pos = Column(String)
    by_hands_tags = Column(String)
    frequency = Column(Float)

    def __repr__(self):
        return "<FrequencyModel(lemma={}, dict_pos={}, pos={}, by_hands_tags={}, frequency={})>".format(
            self.lemma,
            self.dict_pos,
            self.pos,
            self.by_hands_tags,
            self.frequency
        )
