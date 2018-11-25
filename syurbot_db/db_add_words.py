#!/usr/bin/python
# # -*- coding: utf-8 -*-

from syurbot_db.tags_set import TagsSetModel
from syurbot_db.frequency import FrequencyModel
from syurbot_db.word import WordModel
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
from libs.funcs import split_by_words, split_by_sentences

MyWord.required_tags_params = "add_db_rows"


def add_lemma_to_dict(lemma, tags=None, word_register=None, is_normal_form=False, word_source=None, frequency=None):
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
            "word_source": word_source
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
        print("enumerated:", dict_row)


def estimate_frequency(dict_rows_list):
    non_unique_dict_rows_list = []

    for dict_row in dict_rows_list:
        non_unique_dict_row = {
            "word": dict_row["word"],
            "tags_set_num": dict_row["tags_set_num"],
            "tags_info": dict_row["tags_info"],
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
                    d_row["word"] == u_row["word"] and d_row["tags_set_num"] == u_row["tags_set_num"]
            ):
                u_row["frequency"] += d_row["frequency"]
                print("frequency:", d_row)

    for dr in dict_rows_list:
        dict_rows_list.remove(dr)

    dict_rows_list += unique_dict_rows_list


def add_dict_rows(dict_rows_list):

    for dict_row in dict_rows_list:
        SESSION.add(WordModel(
            word=dict_row["word"],
            pos=dict_row["pos"],
            tags_set_num=dict_row["tags_set_num"],
            tags_info=dict_row["tags_info"],
            frequency=dict_row["frequency"],
            word_source=dict_row["word_source"]
        ))

    SESSION.commit()


def add_freq_dict():
    freq_dict_query = SESSION.query(FrequencyModel)
    words_dict_query = SESSION.query(WordModel)
    old_freq_dict = words_dict_query.filter(WordModel.word_source == "freq_dict")
    old_freq_dict.delete(synchronize_session=False)
    dict_rows_list = []

    for row in freq_dict_query:
        print(row)
        dict_rows = add_lemma_to_dict(
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

    add_tags_sets(dict_rows_list)
    enumerate_tags_sets(dict_rows_list)
    estimate_frequency(dict_rows_list)
    add_dict_rows(dict_rows_list)
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

    for sentence in sentences:
            sentence_words = split_by_words(sentence)
            lemma = {"lemma": sentence_words[0], "register": None, "frequency": 1}
            lemms.append(lemma)

            if lemma not in unique_lemms:
                unique_lemms.append(lemma)
                print(lemma)

            for sentence_word in sentence_words[1:]:
                lemma = {"lemma": sentence_word, "register": word_register, "frequency": 1}
                lemms.append(lemma)

                if lemma not in unique_lemms:
                    unique_lemms.append(lemma)
                    print(lemma)

    for unique_lemma in unique_lemms:
        for lemma in lemms:
            if lemma["lemma"] == unique_lemma["lemma"] and lemma["register"] == unique_lemma["register"]:
                unique_lemma["frequency"] += lemma["frequency"]
                print(unique_lemma)

    for lemma in unique_lemms:
        dict_rows = add_lemma_to_dict(
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

    add_tags_sets(dict_rows_list)
    enumerate_tags_sets(dict_rows_list)
    estimate_frequency(dict_rows_list)
    add_dict_rows(dict_rows_list)
    SESSION.commit()
    SESSION.close()
