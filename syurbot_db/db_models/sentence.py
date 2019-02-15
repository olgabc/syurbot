from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from syurbot_db.db_models.source import SourceModel
Base = declarative_base()


class SentenceModel(Base):
    __tablename__ = "sentence"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey(SourceModel.id), nullable=False)
    sentence = Column(String(5000), nullable=False)
    hash = Column(String(32), unique=True, nullable=False)
    sentence_length = Column(Integer, nullable=False)
    fixed_words_qty = Column(Integer, nullable=False)
    trash_words_qty = Column(Integer, nullable=False)

    def __repr__(self):
        return """
        <SentenceModel(sentence={},  
        hash={}, sentence_length={}, fixed_words_qty={},  trash_words_qty={})>
            """.format(
            self.sentence,
            self.hash,
            self.sentence_length,
            self.fixed_words_qty,
            self.trash_words_qty,
        )
