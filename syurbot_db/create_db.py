import pyexcel
from syur_classes import MyWord
from config.config import engine
from syurbot_db.db_models.frequency import FrequencyModel
from syurbot_db.db_models.tag import TagModel
from syurbot_db.db_models.tagset import TagsetModel
from syurbot_db.db_models.tagset_has_tag import TagsetHasTagModel
from syurbot_db.db_models.word import WordModel
from syurbot_db.db_models.source import SourceModel
from syurbot_db.db_models.sentence import SentenceModel
from syurbot_db.db_session import SESSION


def create_tables():
    #FrequencyModel.__table__.create(engine)
    SourceModel.__table__.create(engine)
    TagModel.__table__.create(engine)
    TagsetModel.__table__.create(engine)
    TagsetHasTagModel.__table__.create(engine)
    WordModel.__table__.create(engine)
    SentenceModel.__table__.create(engine)


def add_tag_data():
    opencorp_tags = open("opencorp_tags.txt").readlines()
    tags = [opencorp_tag.rstrip() for opencorp_tag in opencorp_tags] + MyWord.custom_tags

    for tag in tags:
        SESSION.add(TagModel(tag=tag))
    SESSION.commit()


def add_freq_dict_xlsx():
    pyexcel.save_as(file_name="freq_dict.xlsx", name_columns_by_row=0, dest_session=SESSION, dest_table=FrequencyModel)
    SESSION.add(SourceModel(id=1, source="freq_dict"))
    SESSION.commit()


create_tables()
add_tag_data()
#add_freq_dict_xlsx()

"""

"""
