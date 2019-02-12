#!/usr/bin/python
# # -*- coding: utf-8 -*-

from syurbot_db.db_models.word import WordModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from libs.text_funcs import split_by_words, split_by_sentences
from syurbot_db.add_words import get_lexeme_dict_rows, write_words_rows
from syurbot_db.db_models.source_dict import SourceDictModel
from config.config import engine

SourceDictModel.__table__.create(engine)
MyWord.required_tags_params = "add_db_rows"
connection = engine.connect()

def add_source_dict(
        source_id,
        text=None,
        sentences=None,
        is_normal_form=False,
        word_register="get_register"):

    connection.execute(

    )

    if not sentences:
        sentences = split_by_sentences(text)

    connection.execute

def add_word(word, is_first, source_id, firsts_dict, others_dict):
    if is_first:
        try:
            firsts_dict[word]["qty"] += 1
        except IndexError:
            firsts_dict[word] = "todo"

    else:
        try:
            others_dict[word]["qty"] += 1
        except IndexError:
            firsts_dict[word] = "todo"


def add_sentence(sentence, source_id=0):
    sentence_words = split_by_words(sentence)
    sentence_row = {
        'sentence':sentence,
        'length': len(sentence_words),
        'fixed': 0,
        'changable': 0,
        'trash': 0,
        'unchangable': 0,
        'source_id': source_id
    }
    add_word(sentence_words[0], is_first=True, source_id=source_id)

    for sw in sentence_words:
        add_word(sw[0], is_first=True, source_id=source_id)

for p in get_lexeme_dict_rows("испанке", frequency=12): print("ppp", p)