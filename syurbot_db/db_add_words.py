#!/usr/bin/python
# # -*- coding: utf-8 -*-

from syurbot_db.db_models.tagset import TagSetModel
from syurbot_db.db_models.tagset_has_tag import TagSetHasTagModel
from syurbot_db.db_models.frequency import FrequencyModel
from syurbot_db.db_models.word import WordModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from libs.text_funcs import split_by_words, split_by_sentences
from config.config import PSOS_TO_FIND
from sqlalchemy import func
from syurbot_db.db_requests import get_tags_ids, get_tagset_tags_ids

MyWord.required_tags_params = "add_db_rows"


def get_lemma_dict_rows(
        lemma,
        tags=None,
        word_register=None,
        is_normal_form=False,
        word_source=None,
        frequency=None,
        score=None
):
    print("get_lemma_dict_rows:", lemma)
    word_instances_list = []

    word_0 = MyWord(
        lemma,
        tags=tags,
        is_normal_form=is_normal_form,
        word_register=word_register,
        score=score
    )

    if not word_0.parses:
        return

    word_forms = set([(w.normal_form, w.tag.POS) for w in word_0.parses])
    frequency_0 = frequency / len(word_forms)

    if len(word_0.parses) == 1 and word_0.parse_chosen and word_0.parse_chosen.normal_form == word_0.word:
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

            if len(word_1.parses) == 1 and word_1.parse_chosen:
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
            "tags": word_instance[0].all_tags,
            "frequency": word_instance[1],
            "word_source": word_source
        })
        for dr in dict_row["tags"]:
            if dr == dr.upper():
                dict_row["pos"] = dr
                break

        if dict_row["pos"] in PSOS_TO_FIND:
            dict_rows.append(dict_row)

    return dict_rows


def add_tagsets_to_db(dict_rows_list):
    print("ADD_TAGSET")
    tagset_query = SESSION.query(TagSetModel)
    max_tagset_id = int(SESSION.query(func.max(TagSetModel.id))[0][0] or 0)

    tagset_tags_ids_list = []
    db_tagset_tags_ids_list = []

    for dict_row in dict_rows_list:
        print("dict_row", dict_row)
        tagset_tags_ids = ",".join(get_tags_ids(dict_row["tags"], "str"))
        tagset_tags_ids_list.append(tagset_tags_ids)

    tagset_tags_ids_list = list(set(tagset_tags_ids_list))
    tagset_tags_ids_list = [
        set([int(tag_id) for tag_id in tagset.split(",")]) for tagset in tagset_tags_ids_list
    ]

    for tagset in tagset_query:
        tagset_tags_ids = get_tagset_tags_ids(tagset.id)
        db_tagset_tags_ids_list.append(tagset_tags_ids)

    print("tagset_tags_ids_list:", tagset_tags_ids_list)
    print("db_tagset_tags_ids_list:", db_tagset_tags_ids_list)

    for tagset in tagset_tags_ids_list:
        if tagset not in db_tagset_tags_ids_list:
            tagset_id = max_tagset_id + 1
            SESSION.add(TagSetModel(id=tagset_id))

            for tag_id in tagset:
                SESSION.add(TagSetHasTagModel(tagset_id=tagset_id, tag_id=tag_id))

            max_tagset_id += 1

    SESSION.commit()


def enumerate_tagsets(dict_rows_list):
    print("ENUMERATE_TAGS")
    tagset_query = SESSION.query(TagSetModel)
    tagset_tags_ids_list = []

    for tagset in tagset_query:
        tagset_tags_ids = get_tagset_tags_ids(tagset.id)
        tagset_tags_ids_list.append((tagset.id, tagset_tags_ids))

    for dict_row in dict_rows_list:
        dict_tags_ids = get_tags_ids(dict_row["tags"])
        for tagset_id, tags_ids in tagset_tags_ids_list:
            if dict_tags_ids == tags_ids:
                dict_row["tagset_id"] = tagset_id
                print("enumerated:", dict_row)
                break


def add_dict_rows(dict_rows_list):
    print("ADD_DICT_ROWS")
    for dict_row in dict_rows_list:
        SESSION.add(WordModel(
            word=dict_row["word"],
            pos=dict_row["pos"],
            tagset_id=dict_row["tagset_id"],
            frequency=dict_row["frequency"],
            word_source=dict_row["word_source"]
        ))

    SESSION.commit()


def get_unique_rows(word_source):
    words_dict_query = SESSION.query(WordModel)
    words_dict_query = words_dict_query.filter(WordModel.word_source == word_source)
    unique_rows_query = SESSION.query(
        WordModel.word,
        WordModel.pos,
        WordModel.tagset_id,
        func.sum(WordModel.frequency).label('frequency'),
        WordModel.word_source
    ).group_by(
        WordModel.word, WordModel.tagset_id
    ).all()

    words_dict_query.delete(synchronize_session=False)

    for row in unique_rows_query:
        SESSION.add(WordModel(
            word=row.word,
            pos=row.pos,
            tagset_id=row.tagset_id,
            frequency=row.frequency,
            word_source=row.word_source
        ))

        SESSION.commit()


def add_freq_dict():
    freq_dict_query = SESSION.query(FrequencyModel)
    words_dict_query = SESSION.query(WordModel)
    freq_dict_query = freq_dict_query.filter(FrequencyModel.lemma.like('нерв%'))
    old_freq_dict = words_dict_query.filter(WordModel.word_source == "freq_dict")
    old_freq_dict.delete(synchronize_session=False)
    dict_rows_list = []

    for row in freq_dict_query:
        print(row)
        dict_rows = get_lemma_dict_rows(
            lemma=row.lemma,
            tags=row.pos,
            word_register="get_register",
            is_normal_form=True,
            word_source="freq_dict",
            frequency=row.frequency
        )

        if not dict_rows:
            continue

        dict_rows_list += dict_rows

    add_tagsets_to_db(dict_rows_list)
    enumerate_tagsets(dict_rows_list)
    add_dict_rows(dict_rows_list)
    get_unique_rows("freq_dict")

    SESSION.commit()
    SESSION.close()


def add_dict(
        word_source,
        text=None,
        sentences=None,
        is_normal_form=False,
        word_register="get_register"):

    words_dict_query = SESSION.query(WordModel)
    old_dict = words_dict_query.filter(WordModel.word_source == word_source)
    old_dict.delete(synchronize_session=False)

    if not sentences:
        sentences = split_by_sentences(text)

    dict_rows_list = []
    lemms = []
    unique_lemms = []
    non_register_lemms = []
    register_lemms = []

    for sentence in sentences:
        sentence_words = split_by_words(sentence)
        non_register_lemms.append(sentence_words[0])
        lemms.append({"lemma": sentence_words[0], "register": None})

        for sentence_word in sentence_words[1:]:
            register_lemms.append(sentence_word)
            lemms.append({"lemma": sentence_word, "register": word_register})

    unique_register_lemms = list(set(register_lemms))
    unique_non_register_lemms = list(set(non_register_lemms))

    for lemma in unique_register_lemms:
        lemma_dict = {"lemma": lemma, "register": word_register, "frequency": register_lemms.count(lemma)}
        unique_lemms.append(lemma_dict)
        print("register", lemma_dict)

    for lemma in unique_non_register_lemms:
        lemma_dict = {"lemma": lemma, "register": None, "frequency": non_register_lemms.count(lemma)}
        unique_lemms.append(lemma_dict)
        print("non_register", lemma_dict)

    for lemma in unique_lemms:
        dict_rows = get_lemma_dict_rows(
            lemma=lemma["lemma"],
            word_register=lemma["register"],
            is_normal_form=is_normal_form,
            word_source=word_source,
            frequency=lemma["frequency"],
            score=0.01
        )
        if not dict_rows:
            continue

        dict_rows_list += dict_rows

    add_tagsets_to_db(dict_rows_list)
    enumerate_tagsets(dict_rows_list)
    add_dict_rows(dict_rows_list)
    get_unique_rows(word_source)
    SESSION.commit()
    SESSION.close()
