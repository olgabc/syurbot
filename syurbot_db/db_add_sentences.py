#!/usr/bin/python
# # -*- coding: utf-8 -*-

import re
from syurbot_db.sentence import SentenceModel
from syur_classes import MyWord
from libs.funcs import split_by_sentences, split_by_words

MyWord.required_tags_params = "add_db_rows"


def add_sentences(name_without_extension, folder="books"):
    sentences = split_by_sentences(name_without_extension, folder)

    for sentence in sentences:
        sentence_words = re.sub(r'[^-A-яA-z\s\d]|(?<![A-яA-z](?=.[A-яA-z]))-', "", sentence)
        sentence_words = re.sub(r'(\s+)', " ", sentence_words)
        sentence_words = re.sub(r'(^\s|\s$)', "", sentence_words)
        sentence_words = sentence_words.split(" ")
        sentence_length = len(sentence_words)

        #sentences_insert.execute({
            #'sentence': sentence,
            #'sentence_length': sentence_length,
            #'source': name_without_extension
        #})


from config.config import engine
SentenceModel.__table__.drop(engine)
SentenceModel.__table__.create(engine)

