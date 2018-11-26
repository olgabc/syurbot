from config.config import engine
from syurbot_db.tagset import TagSetModel
from syurbot_db.word import WordModel
from syurbot_db.db_add_words import add_freq_dict, add_dict
from libs.funcs import load_some_text
# from syurbot_db.db_add_sentences import add_sentences

"""
TagsSetModel.__table__.drop(engine)
TagsSetModel.__table__.create(engine)

WordModel.__table__.drop(engine)
WordModel.__table__.create(engine)


add_freq_dict()

"""

#text = load_some_text("ann_kar")
#add_dict(word_source="ann_kar", text=text)
add_dict(word_source="test", text="обиженный и обозленный паша lфыва me ушел к испанке испанке испанке. Испанке. Испанка")