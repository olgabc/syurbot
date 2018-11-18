from config.config import engine
import re
import os
from sqlalchemy import Table, MetaData
from sqlalchemy.orm import sessionmaker
from db_classes import FreqDict, WordsDict
from syur_classes import MyWord
import json

metadata = MetaData(engine)
Session = sessionmaker(bind=engine)


def split_book_by_sentences(name_without_extension, folder="books"):
    file_path = os.path.join(
        folder,
        "{}.txt".format(name_without_extension)
    )
    book = open(file_path)
    book = book.read()
    book = book.replace(
        "\n", " "
    ).replace(
        "—", "–"
    ).replace(
        "…", "..."
    )
    book = re.sub(r'([.!?])([^.])', r'\1@\2', book)
    book = re.sub(r'@([^А-яA-z]*\b[а-яa-z])', r' \1', book)
    book = re.sub(r'(\b[А-яA-z]{,3}\b)@', r'\1 ', book)
    book = re.sub(r'(\s+)', " ", book)
    book = re.sub(r'(\b-\s|\s-\b)', " - ", book)
    book = re.sub(r'(@\s)', "@", book)
    book = book.split("@")
    book_indexes = range(len(book))

    for i in book_indexes:

        if "«" in book[i] and "»" not in book[i]:

            for cnt in range(1, 11):
                book[i] += " {}".format(book[i+cnt])
                book[i+cnt] = "to_delete"
                if "»" in book[i]:
                    break

    return [sentence for sentence in book if sentence != "to_delete"]


def insert_sentences_to_db(name_without_extension, folder="books"):
    sentences = split_book_by_sentences(name_without_extension, folder)

    for sentence in sentences:
        sentence_words = re.sub(r'[^-A-яA-z\s\d]|(?<![A-яA-z](?=.[A-яA-z]))-', "", sentence)
        sentence_words = re.sub(r'(\s+)', " ", sentence_words)
        sentence_words = re.sub(r'(^\s|\s$)', "", sentence_words)
        sentence_words = sentence_words.split(" ")
        sentence_length = len(sentence_words)

        sentences_insert.execute({
            'sentence': sentence,
            'sentence_length': sentence_length,
            'source': name_without_extension
        })


def add_freq_dict():
    session = Session()
    freq_dict_query = session.query(FreqDict)
    words_dict_query = session.query(WordsDict)
    old_freq_dict = words_dict_query.filter(WordsDict.words_dict_json.like('%"source": "freq_dict"%'))
    old_freq_dict.delete(synchronize_session=False)

    for row in freq_dict_query:
        word = MyWord(
            word=row.lemma,
            tags=row.pos,
            is_normal_form=True,
            word_register="get_register"
        )
        dict_row = ""

        if row.pos == "NOUN" and word.parses and len(word.parses) > 1:

            for parse in word.parses:
                tag = str(parse.tag).replace(" ", ",").split(",")

                if "multianim" in word.all_tags:
                    tag.append("multianim")
                dict_row = {
                    "lemma": row.lemma,
                    "pos": row.pos,
                    "all_tags": MyWord(
                        word=row.lemma,
                        tags=tag,
                        is_normal_form=True,
                        word_register="get_register"
                    ).all_tags,
                    "frequency": row.frequency,
                    "source": "freq_dict"
                }
        else:
            dict_row = {
                "lemma": row.lemma,
                "pos": row.pos,
                "all_tags": word.all_tags,
                "frequency": row.frequency,
                "source": "freq_dict"
            }

        json_row = json.dumps(dict_row, ensure_ascii=False)
        session.add(WordsDict(words_dict_json=json_row))

    session.commit()
    session.close()


session = Session()
session.add(FreqDict(lemma="нервически",pos="ADVB"))
session.commit()


def add_dict(words, source, tags=None, is_normal_form=False, word_register="get_register"):

    unique_words = set(words)
    len_words = len(words)

    if not tags:
        tags = []

    for word in unique_words:
        word = MyWord(word, tags=tags, is_normal_form=is_normal_form, word_register=word_register)
        frequency = words.count(word)/len_words

        if word.parse_chosen:
            print(
                word.parse_chosen.normal_form,
                row[frequency_dict.c.pos],
                word.all_tags,
                frequency,
                source
            )

            for parse in word.parses:
                tag = str(parse.tag).replace(" ", ",").split(",")

                if "multianim" in word.all_tags:
                    tag.append("multianim")
                print(
                    row[frequency_dict.c.lemma],
                    row[frequency_dict.c.pos],
                    MyWord(
                        word=row[frequency_dict.c.lemma],
                        tags=tag,
                        is_normal_form=True,
                        word_register="get_register"
                    ).all_tags,
                    row[frequency_dict.c.frequency],
                    source
                )
        else:
            print(
                row[frequency_dict.c.lemma],
                row[frequency_dict.c.pos],
                word.all_tags,
                row[frequency_dict.c.frequency],
                source
            )