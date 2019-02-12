#!/usr/bin/python
# # -*- coding: utf-8 -*-

from syurbot_db.db_models.sentence import SentenceModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from libs.text_funcs import split_by_words, split_by_sentences
from syurbot_db.add_words import get_lexeme_dict_rows, write_words_rows

def add_sentences(word_source, text=None, sentences=None):
    if not sentences:
        sentences = split_by_sentences(text)

    for sentence in sentences:
        sentence_words = split_by_words(sentence)
        sentence_length = len(sentence_words)
        sentence_words_check = [MyWord(sentence_words[0], word_register=None).get_check_result()]

        for sentence_word in sentence_words[1:]:
            sentence_words_check.append(MyWord(sentence_word, word_register="get_register").get_check_result())

        fixed_words_qty = sentence_words_check.count("fixed")
        trash_words_qty = sentence_words_check.count("trash")
        unchangable_words_qty = sentence_words_check.count("unchangable")

        SESSION.add(SentenceModel(
            sentence=sentence,
            sentence_length=sentence_length,
            fixed_words_qty=fixed_words_qty,
            trash_words_qty=trash_words_qty,
            unchangable_words_qty=unchangable_words_qty,
            word_source=word_source
        ))

    SESSION.commit()
    SESSION.close()
