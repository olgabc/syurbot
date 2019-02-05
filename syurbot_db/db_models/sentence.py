from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from syurbot_db.db_models.source import SourceModel
Base = declarative_base()


class SentenceModel(Base):
    __tablename__ = "sentence"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey(SourceModel.id))
    sentence = Column(String(5000))
    sentence_length = Column(Integer)
    fixed_words_qty = Column(Integer)
    trash_words_qty = Column(Integer)
    unchangable_words_qty = Column(Integer)

    def __repr__(self):
        return """
        <SentenceModel(sentence={},  
        sentence_length={}, fixed_words_qty={},  trash_words_qty={}, unchangable_words_qty={})>
            """.format(
            self.sentence,
            self.sentence_length,
            self.fixed_words_qty,
            self.trash_words_qty,
            self.unchangable_words_qty
        )
