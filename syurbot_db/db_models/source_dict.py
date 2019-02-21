from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class SourceDictModel(Base):
    __tablename__ = "source_dict"
    id = Column(Integer, primary_key=True)
    lexeme = Column(String(50), nullable=False)
    is_first = Column(Boolean, default=0)
    tags = Column(String(200), nullable=False)
    hash = Column(String(32), unique=True, nullable=False)
    type = Column(String(10))
    frequency = Column(Float, nullable=False)

    def __repr__(self):
        return "<SourceDictModel(lexeme={}, is_first={}, tags = {}, hash={}, type={}, frequency={})>".format(
            self.lexeme,
            self.is_first,
            self.tags,
            self.hash,
            self.type,
            self.frequency
        )
