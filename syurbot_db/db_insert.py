from config.config import engine
from syurbot_db.tagset import TagSetModel
from syurbot_db.tag import TagModel
from syurbot_db.word import WordModel
from syurbot_db.db_add_words import add_freq_dict, add_dict
from libs.funcs import load_some_text
# from syurbot_db.db_add_sentences import add_sentences


TagSetModel.__table__.drop(engine)
TagSetModel.__table__.create(engine)

WordModel.__table__.drop(engine)
WordModel.__table__.create(engine)


add_freq_dict()

"""

text = load_some_text("ann_kar")
add_dict(word_source="ann_kar", text=text)
"""