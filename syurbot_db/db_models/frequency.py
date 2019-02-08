from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class FrequencyModel(Base):
    __tablename__ = "frequency"
    id = Column(Integer, primary_key=True)
    lexeme = Column(String(50))
    tags = Column(String(200))
    frequency = Column(Float)

    def __repr__(self):
        return "<FrequencyModel(lexeme={}, tags={}, frequency={})>".format(
            self.lexeme,
            self.tags,
            self.frequency
        )
