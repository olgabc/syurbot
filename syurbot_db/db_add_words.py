#!/usr/bin/python
# # -*- coding: utf-8 -*-

from syurbot_db.tag import TagModel
from syurbot_db.tagset import TagSetModel
from syurbot_db.tagset_has_tag import TagSetHasTagModel
from syurbot_db.frequency import FrequencyModel
from syurbot_db.word import WordModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from libs.funcs import split_by_words, split_by_sentences
from config.config import PSOS_TO_FIND
from sqlalchemy import func
import hashlib

MyWord.required_tags_params = "add_db_rows"


def get_lemma_dict_rows(lemma, tags=None, word_register=None, is_normal_form=False, word_source=None, frequency=None):
    print("lemma:", lemma)
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
    tag_query = SESSION.query(TagModel)
    tagset_query = SESSION.query(TagSetModel)
    tagsethastag_query = SESSION.query(TagSetHasTagModel)
    max_tagset_id = int(SESSION.query(func.max(TagSetModel.id))[0][0])

    tag_dict = {row.tag.strip(): row.id for row in tag_query}
    tagset_tag_ids_list = []
    db_tagset_tag_ids_list = []

    for dict_row in dict_rows_list:
        tagset = dict_row["tags"]
        tagset_tag_ids = ",".join([str(tag_dict[tag_name]) for tag_name in tagset])
        tagset_tag_ids_list.append(tagset_tag_ids)

    tagset_tag_ids_list = list(set(tagset_tag_ids_list))

    for tagset in tagset_query:
        tagset_tags_query = tagsethastag_query.filter(TagSetHasTagModel.tagset_id == tagset.id)
        tagset_tag_ids = set([row.tag_id for row in tagset_tags_query])
        db_tagset_tag_ids_list.append(tagset_tag_ids)

    for tagset in tagset_tag_ids_list:
        tagset = set([int(tag_id) for tag_id in tagset.split(",")])
        if tagset not in db_tagset_tag_ids_list:
            SESSION.add(TagSetModel())
            SESSION.commit()
            tagset_id = max_tagset_id + 1

            for tag_id in tagset:
                SESSION.add(TagSetHasTagModel(tagset_id=tagset_id, tag_id=tag_id))
                print("tagset", tagset_id, "tag_id", tag_id)

            max_tagset_id += 1

    SESSION.commit()


def enumerate_tagsets(dict_rows_list):
    tag_query = SESSION.query(TagModel)
    tagset_query = SESSION.query(TagSetModel)
    tagsethastag_query = SESSION.query(TagSetHasTagModel)
    tag_dict = {row.tag.strip(): row.id for row in tag_query}
    tagset_tags_list = []

    for tagset in tagset_query:
        tagset_tags_query = tagsethastag_query.filter(TagSetHasTagModel.tagset_id == tagset.id)
        tagset_tag_id = [row.tag_id for row in tagset_tags_query]
        tagset_tags_list.append((tagset.id, set(tagset_tag_id)))

    for dict_row in dict_rows_list:
        dict_row["tag_ids"] = set([tag_dict[tag_name] for tag_name in dict_row["tags"]])
        for tagset_id, tag_ids in tagset_tags_list:
            if dict_row["tag_ids"] == tag_ids:
                dict_row["tagset_id"] = tagset_id
                print("enumerated:", dict_row)
                break


def add_dict_rows(dict_rows_list):

    for dict_row in dict_rows_list:
        SESSION.add(WordModel(
            word=dict_row["word"],
            pos=dict_row["pos"],
            tagset_id=dict_row["tagset_id"],
            frequency=dict_row["frequency"],
            word_source=dict_row["word_source"]
        ))

    SESSION.commit()


def get_unique_rows(dict_rows_list):
    non_unique_dict_rows_list = []

    for dict_row in dict_rows_list:
        non_unique_dict_row = {
            "word": dict_row["word"],
            "tagset_id": dict_row["tagset_id"],
            "tags": dict_row["tags"],
            "word_source": dict_row["word_source"],
            "pos": dict_row["pos"],
            "frequency": 0
        }
        non_unique_dict_rows_list.append(non_unique_dict_row)
        print("non_unique:", non_unique_dict_row)

    unique_dict_rows_list = []

    for nu_row in non_unique_dict_rows_list:
        if nu_row not in unique_dict_rows_list:
            unique_dict_rows_list.append(nu_row)
            print("unique:", nu_row)

    for u_row in unique_dict_rows_list:
        for d_row in dict_rows_list:
            if (
                    d_row["word"] == u_row["word"] and d_row["tagset_id"] == u_row["tagset_id"]
            ):
                u_row["frequency"] += d_row["frequency"]
                print("frequency:", d_row)

    for dr in dict_rows_list:
        dict_rows_list.remove(dr)

    dict_rows_list += unique_dict_rows_list


def add_freq_dict():
    freq_dict_query = SESSION.query(FrequencyModel)
    freq_dict_query = freq_dict_query.filter(FrequencyModel.lemma.like('нерв%'))  #temp
    words_dict_query = SESSION.query(WordModel)
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
    #get_unique_rows(dict_rows_list)

    SESSION.commit()
    SESSION.close()


def add_dict(
        word_source,
        text=None,
        sentences=None,
        tags=None,
        is_normal_form=False,
        word_register="get_register"):

    words_dict_query = SESSION.query(WordModel)
    old_dict = words_dict_query.filter(WordModel.word_source == word_source)
    old_dict.delete(synchronize_session=False)

    if not tags:
        tags = []

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
            tags=tags,
            word_register=lemma["register"],
            is_normal_form=is_normal_form,
            word_source=word_source,
            frequency=lemma["frequency"]
        )
        if not dict_rows:
            continue

        dict_rows_list += dict_rows

    add_tagsets_to_db(dict_rows_list)
    enumerate_tagsets(dict_rows_list)
    add_dict_rows(dict_rows_list)
    get_unique_rows(dict_rows_list)
    SESSION.commit()
    SESSION.close()
