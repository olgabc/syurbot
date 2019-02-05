from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class FrequencyModel(Base):
    __tablename__ = "frequency"
    id = Column(Integer, primary_key=True)
    lemma = Column(String(50))
    tags = Column(String(200))
    frequency = Column(Float)

    def __repr__(self):
        return "<FrequencyModel(lemma={}, tags={}, frequency={})>".format(
            self.lemma,
            self.tags,
            self.frequency
        )
