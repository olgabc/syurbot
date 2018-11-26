#!/usr/bin/python
# # -*- coding: utf-8 -*-
import csv
from syur_classes import MyWord
from config.config import engine
from syurbot_db.frequency import FrequencyModel
from syurbot_db.tag import TagModel
from syurbot_db.tagset import TagSetModel
from syurbot_db.tagset_has_tag import TagSetHasTagModel
from syurbot_db.word import WordModel
from syurbot_db.sentence import SentenceModel
from syurbot_db.db_session import SESSION
from sqlalchemy.ext.declarative import declarative_base


"""
FrequencyModel.__table__.create(engine)
TagModel.__table__.create(engine)
TagSetModel.__table__.create(engine)
TagSetHasTagModel.__table__.create(engine)
WordModel.__table__.create(engine)
SentenceModel.__table__.create(engine)

opencorp_tags = open("opencorp_tags.txt").readlines()
tags = opencorp_tags + MyWord.custom_tags

for tag in tags:
    SESSION.add(TagModel(tag=tag))
SESSION.commit()

"""


def add_frequency_data():

    dict_rows = []
    with open("freq_dict.csv", 'r', encoding='utf-8') as freq_dict:
        file_dialect = csv.Sniffer().sniff(freq_dict.read(1024))
        freq_dict.seek(0)
        dict_reader = csv.DictReader(freq_dict, dialect=file_dialect)

        for dict_row in dict_reader:
            dict_row = dict(dict_row)
            dict_row["lemma"] = dict_row.pop("\ufefflemma")
            dict_row["frequency"] = float(dict_row["frequency"].replace(",", "."))
            dict_rows.append(dict_row)

    for dict_row in dict_rows:
        SESSION.add(
            FrequencyModel(
                lemma=dict_row["lemma"],
                dict_pos=dict_row["dict_pos"],
                pos=dict_row["pos"],
                by_hands_tags=dict_row["by_hands_tags"],
                frequency=float(dict_row["frequency"])
            )
        )

    SESSION.commit()


add_frequency_data()
