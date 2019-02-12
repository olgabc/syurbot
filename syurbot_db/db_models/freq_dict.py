from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class FrequencyDictModel(Base):
    __tablename__ = "frequency"
    id = Column(Integer, primary_key=True)
    lexeme = Column(String(50), nullable=False)
    tags = Column(String(200), nullable=False)
    frequency = Column(Float, nullable=False)

    def __repr__(self):
        return "<FrequencyModel(lexeme={}, tags={}, frequency={})>".format(
            self.lexeme,
            self.tags,
            self.frequency
        )
