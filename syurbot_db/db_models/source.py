from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class SourceModel(Base):
    __tablename__ = "source"
    id = Column(Integer, primary_key=True)
    source = Column(String(500), nullable=False)

    def __repr__(self):
        return "<SourceModel(source={})>".format(self.source)
