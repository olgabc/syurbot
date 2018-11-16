from config.config import engine
from syur_classes import MyWord
from sqlalchemy import Table, MetaData
from sqlalchemy.sql import select
import json

metadata = MetaData(engine)
conn = engine.connect()

fd = Table('fd', metadata, autoload=True)

words_dict = Table('words_dict', metadata, autoload=True)
words_dict_insert = words_dict.insert()

select_fd = select([fd.c.lemma, fd.c.pos, fd.c.frequency])
select_fd_result = conn.execute(select_fd)


def add_freq_dict():
    for row in select_fd_result:
        word = MyWord(word=row[fd.c.lemma], tags=row[fd.c.pos], is_normal_form=True, word_register="get_register")
        if row[fd.c.pos] == "NOUN" and word.parses and len(word.parses) > 1:

            for parse in word.parses:
                tag = str(parse.tag).replace(" ", ",").split(",")

                if "multianim" in word.all_tags:
                    tag.append("multianim")
                dict_row = {
                    "lemma": row[fd.c.lemma],
                    "pos": row[fd.c.pos],
                    "all_tags": MyWord(
                        word=row[fd.c.lemma],
                        tags=tag,
                        is_normal_form=True,
                        word_register="get_register"
                    ).all_tags,
                    "frequency": row[fd.c.frequency],
                    "sourse": "freq_dict"
                }
        else:
            dict_row = {
                "lemma": row[fd.c.lemma],
                "pos": row[fd.c.pos],
                "all_tags": word.all_tags,
                "frequency": row[fd.c.frequency],
                "sourse": "freq_dict"
            }

        json_row = json.dumps(dict_row)
        print(json_row)
        words_dict_insert.execute(json_row)


    select_fd_result.close()

add_freq_dict()


def add_dict(words, source, tags=None, is_normal_form=False, word_register="get_register"):

    unique_words = set(words)
    len_words = len(words)

    if not tags:
        tags=[]

    for word in unique_words:
        word = MyWord(word, tags=tags, is_normal_form=is_normal_form, word_register=word_register)
        frequency = words.count(word)/len_words

        if word.parse_chosen:
            print(
                word.parse_chosen.normal_form,
                row[fd.c.pos],
                word.all_tags,
                frequency,
                source
            )

            for parse in word.parses:
                tag = str(parse.tag).replace(" ", ",").split(",")

                if "multianim" in word.all_tags:
                    tag.append("multianim")
                print(
                    row[fd.c.lemma],
                    row[fd.c.pos],
                    MyWord(
                        word=row[fd.c.lemma],
                        tags=tag,
                        is_normal_form=True,
                        word_register="get_register"
                    ).all_tags,
                    row[fd.c.frequency],
                    source
                )
        else:
            print(
                row[fd.c.lemma],
                row[fd.c.pos],
                word.all_tags,
                row[fd.c.frequency],
                source
            )
