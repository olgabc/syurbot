from config.config import engine
from syurbot_db.tags_set import TagsSetModel
from syurbot_db.word import WordModel
from syurbot_db.db_add_words import add_freq_dict, add_dict
# from syurbot_db.db_add_sentences import add_sentences

TagsSetModel.__table__.drop(engine)
TagsSetModel.__table__.create(engine)

WordModel.__table__.drop(engine)
WordModel.__table__.create(engine)
add_freq_dict()
add_dict(source="test")
