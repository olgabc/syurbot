#!/usr/bin/python
# -*- coding: utf-8 -*-


import pyexcel
from syurbot_db.db_models.source import SourceModel
from config.config import engine
from syurbot_db.add_words import get_lexeme_dict_rows, write_words_rows, group_word_temp_rows
from syurbot_db.db_models.freq_dict import FrequencyDictModel
from syurbot_db.db_session import SESSION


connection = engine.connect()


def add_freq_dict_xlsx():
    pyexcel.save_as(
        file_name="freq_dict.xlsx",
        name_columns_by_row=0,
        dest_session=SESSION,
        dest_table=FrequencyDictModel
    )
    SESSION.add(SourceModel(id=1, source="freq_dict"))
    SESSION.commit()


def get_freq_dict_rows():
    freq_dict_query = connection.execute(
        """
        SELECT * 
        FROM freq_dict
        """
    )
    rows = []

    for freq_dict_row in freq_dict_query:
        rows += get_lexeme_dict_rows(
            lexeme=freq_dict_row.lexeme,
            tags=set(freq_dict_row.tags.split(",")),
            word_register="get_register",
            is_normal_form=True,
            source_id=1,
            frequency=freq_dict_row.frequency,
            purpose="add_db_freq_dict"
        )

    return rows


"""
add_freq_dict_xlsx()
freq_dict_rows = get_freq_dict_rows()
write_words_rows(freq_dict_rows)
"""


