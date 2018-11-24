#!/usr/bin/python
# # -*- coding: utf-8 -*-

import re
from syurbot_db.tags_set import TagsSetModel
from syurbot_db.frequency import FrequencyModel
from syurbot_db.word import WordModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from libs.funcs import split_by_words, split_by_sentences

MyWord.required_tags_params = "add_db_rows"


def add_lemma_to_dict(lemma, tags=None, word_register=None, is_normal_form=False, source=None, frequency=1):
    word_instances_list = []

    word_0 = MyWord(
        lemma,
        tags=tags,
        is_normal_form=is_normal_form,
        word_register=word_register
    )

    if not word_0.parses:
        return

    word_forms = set([(w.normal_form, w.tag.POS) for w in word_0.parses])
    frequency_0 = frequency / len(word_forms)

    if len(word_0.parses) == 1 and word_0.parse_chosen.normal_form == word_0.word:
        word_instances_list.append((word_0, frequency_0))
    
    else:
        for word_form in word_forms:
    
            word_1 = MyWord(
                word=word_form[0],
                tags=word_form[1],
                is_normal_form=True,
                word_register=word_register
            )

            if not word_1.parses:
                continue

            frequency_1 = frequency_0 / len(word_1.parses)

            if len(word_1.parses) == 1:
                word_instances_list.append((word_1, frequency_1))
    
            else:
                for parse in word_1.parses:
                    parse_tag = str(parse.tag).replace(" ", ",").split(",") + word_1.custom_tags
                    word_2 = MyWord(
                        word=word_form[0],
                        tags=parse_tag,
                        is_normal_form=True,
                        word_register=word_register
                    )

                    if not word_2.parses:
                        continue

                    frequency_2 = frequency_1 / len(word_2.parses)
    
                    if word_2.parse_chosen:
                        word_instances_list.append((word_2, frequency_2))

    dict_rows = []

    for word_instance in word_instances_list:
        dict_row = ({
            "word": word_instance[0].word,
            "tags_set_num": 0,
            "tags_info": word_instance[0].all_tags,
            "frequency": word_instance[1],
            "source": source
        })
        for dr in dict_row["tags_info"]:
            if dr == dr.upper():
                dict_row["pos"] = dr

        dict_rows.append(dict_row)

    for dict_row in dict_rows:
        dict_row["tags_info"] = ",".join(dict_row["tags_info"])

    return dict_rows


def add_tags_sets(dict_rows_list):

    tags_set_query = SESSION.query(TagsSetModel)
    tags_sets_list = []

    for tags_set_row in tags_set_query:
        tags_sets_list.append(tags_set_row.tags_set)

    tags_sets = []
    
    for dict_row in dict_rows_list:
        tags_sets.append(dict_row["tags_info"])

    unique_tags_sets = list(set(tags_sets))

    for tag_set in unique_tags_sets:
        if tag_set not in tags_sets_list:
            SESSION.add(TagsSetModel(tags_set=tag_set))

    SESSION.commit()


def enumerate_tags_sets(dict_rows_list):
    tags_set_query = SESSION.query(TagsSetModel)
    tags_sets_dict = {}

    for tags_set_row in tags_set_query:
        tags_sets_dict[tags_set_row.tags_set] = tags_set_row.id

    for dict_row in dict_rows_list:
        dict_row["tags_set_num"] = tags_sets_dict[dict_row["tags_info"]]


def estimate_frequency(dict_rows_list):
    for dict_row in dict_rows_list:
        frequency_multiplier = len([
            dr for dr in dict_rows_list if (
                dr["word"] == dict_row["word"] and dr["tags_set_num"] == dict_row["tags_set_num"]
            )
        ])
        dict_row["frequency"] *= frequency_multiplier


def add_dict_rows(dict_rows_list):
    unique_dict_rows_list = []

    for dict_row in dict_rows_list:
        if dict_row not in unique_dict_rows_list:
            SESSION.add(WordModel(
                word=dict_row["word"],
                pos=dict_row["pos"],
                tags_set_num=dict_row["tags_set_num"],
                tags_info=dict_row["tags_info"],
                frequency=dict_row["frequency"],
                source=dict_row["source"]
            ))
            unique_dict_rows_list.append(dict_row)

    SESSION.commit()


def add_freq_dict():
    freq_dict_query = SESSION.query(FrequencyModel)
    words_dict_query = SESSION.query(WordModel)
    old_freq_dict = words_dict_query.filter(WordModel.source == "freq_dict")
    old_freq_dict.delete(synchronize_session=False)
    dict_rows_list = []

    for row in freq_dict_query:
        print(row)
        dict_rows = add_lemma_to_dict(
            lemma=row.lemma,
            tags=row.pos,
            word_register="get_register",
            is_normal_form=True,
            source="freq_dict",
            frequency=row.frequency
        )

        if not dict_rows:
            continue

        dict_rows_list += dict_rows

    add_tags_sets(dict_rows_list)
    enumerate_tags_sets(dict_rows_list)
    estimate_frequency(dict_rows_list)
    add_dict_rows(dict_rows_list)
    SESSION.commit()
    SESSION.close()


def add_dict(text, source, tags=None, is_normal_form=False, word_register="get_register", frequency=1):

    words_dict_query = SESSION.query(WordModel)
    old_dict = words_dict_query.filter(WordModel.source == source)
    old_dict.delete(synchronize_session=False)

    if not tags:
        tags = []

    sentences = split_by_sentences(text)

    dict_rows_list = []
    lemms = []

    for sentence in sentences:
            sentence_words = split_by_words(sentence)
            lemms.append({"lemma": sentence_words[0], "register": None})

            for sentence_word in sentence_words[1:]:
                lemms.append({"lemma": sentence_word, "register": word_register})

    for lemma in lemms:
        dict_rows = add_lemma_to_dict(
            lemma=lemma["lemma"],
            tags=tags,
            word_register=lemma["register"],
            is_normal_form=is_normal_form,
            source=source,
            frequency=frequency
        )
        dict_rows_list += dict_rows

    add_tags_sets(dict_rows_list)
    enumerate_tags_sets(dict_rows_list)
    estimate_frequency(dict_rows_list)
    add_dict_rows(dict_rows_list)
    SESSION.commit()
    SESSION.close()

def insert_sentences_to_db(name_without_extension, folder="books"):
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




"""
tag_set_query = SESSION.query(TagsSetModel)
tag_set_query.delete(synchronize_session=False)
SESSION.commit()
"""
from config.config import engine
TagsSetModel.__table__.drop(engine)
TagsSetModel.__table__.create(engine)

WordModel.__table__.drop(engine)
WordModel.__table__.create(engine)
add_freq_dict()
#add_dict("Вася обиделся. Обидевшийся, обозленный и зеленый Паша ушел к испанке испанке испанке испанке", source="test")
#add_dict("амфибия", "test")

#TODO if not refl убрать "ся"