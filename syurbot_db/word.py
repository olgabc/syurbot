from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class WordModel(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    word_json = Column(String)

    def __repr__(self):
        return "<WordModel(words_dict={})>".format(self.words_dict_json)
