import re
import os
from syurbot_db.frequency import FrequencyModel
from syurbot_db.word import WordModel
# from syurbot_db.sentence import SentenceModel
from sqlalchemy.sql import and_
from syurbot_db.db_session import SESSION
from syur_classes import MyWord
import json


def load_some_text(name_without_extension, folder="books"):
    file_path = os.path.join(
        folder,
        "{}.txt".format(name_without_extension)
    )
    book = open(file_path)
    return book.read()


def split_by_sentences(text):
    text = text.replace(
        "\n", " "
    ).replace(
        "—", "–"
    ).replace(
        "…", "..."
    )
    text = re.sub(r'([.!?])([^.])', r'\1@\2', text)
    text = re.sub(r'@([^А-яA-z]*\b[а-яa-z])', r' \1', text)
    text = re.sub(r'(\b[А-яA-z]{,3}\b)@', r'\1 ', text)
    text = re.sub(r'(\s+)', " ", text)
    text = re.sub(r'(\b-\s|\s-\b)', " - ", text)
    text = re.sub(r'(@\s)', "@", text)
    text = text.split("@")
    text_indexes = range(len(text))

    for i in text_indexes:

        if "«" in text[i] and "»" not in text[i]:

            for cnt in range(1, 11):
                text[i] += " {}".format(text[i+cnt])
                text[i+cnt] = "to_delete"
                if "»" in text[i]:
                    break

    return [sentence for sentence in text if sentence != "to_delete"]


def split_by_words(text):

    text = re.sub(r'[^-A-яA-z\s\d]|(?<![A-яA-z](?=.[A-яA-z]))-', "", text)
    text = re.sub(r'(\s+)', " ", text)
    text = re.sub(r'(^\s|\s$)', "", text)
    words = text.split(" ")
    return words


def add_freq_dict():
    freq_dict_query = SESSION.query(FrequencyModel)
    words_dict_query = SESSION.query(WordModel)
    old_freq_dict = words_dict_query.filter(WordModel.word_json.like('%"source": "freq_dict"%'))
    old_freq_dict.delete(synchronize_session=False)
    dict_rows = []

    for row in freq_dict_query:

        word = MyWord(
            word=row.lemma,
            tags=row.pos,
            is_normal_form=True,
            word_register="get_register"
        )
        print("word:", word.word)

        if word.parses:
            frequency = (row.frequency or 0) / len(set([(w.normal_form, w.tag.POS) for w in word.parses]))

            if "multianim" in word.all_tags:
                frequency = frequency / 2
        else:
            frequency = 1

        if row.pos == "NOUN" and word.parses and len(word.parses) > 1:

            for parse in word.parses:
                tag = str(parse.tag).replace(" ", ",").split(",")

                tag += word.extra_tags

                myword = MyWord(
                        word=row.lemma,
                        tags=tag,
                        is_normal_form=True,
                        word_register="get_register"
                    )
                dict_row = {
                    "lemma": row.lemma,
                    "pos": row.pos,
                    "tags": myword.required_tags + myword.extra_tags,
                    "frequency": frequency,
                    "source": "freq_dict"
                }

                if myword.parse_chosen and myword.parse_chosen.tag.animacy:
                    dict_row["tags"].append(myword.parse_chosen.tag.animacy)

                dict_row["tags"] = set(dict_row["tags"])

                if dict_row not in dict_rows:
                    dict_rows.append(dict_row)

        else:
            dict_row = {
                "lemma": row.lemma,
                "pos": row.pos,
                "tags": word.required_tags + word.extra_tags,
                "frequency": row.frequency,
                "source": "freq_dict"
            }

            if word.parse_chosen and word.parse_chosen.tag.animacy:
                dict_row["tags"].append(word.parse_chosen.tag.animacy)

            dict_row["tags"] = set(dict_row["tags"])

            if dict_row not in dict_rows:
                dict_rows.append(dict_row)

    for d_row in dict_rows:
        d_row["tags"] = sorted(list(d_row["tags"]))
        json_row = json.dumps(d_row, ensure_ascii=False)
        SESSION.add(WordModel(word_json=json_row))
    
    SESSION.commit()
    SESSION.close()


def add_dict(text, source, tags=None, is_normal_form=False, word_register="get_register"):

    words_dict_query = SESSION.query(WordModel)
    old_dict = words_dict_query.filter(WordModel.word_json.like('%"source": "{}"%'.format(source)))
    old_dict.delete(synchronize_session=False)
    dict_rows = []

    if not tags:
        tags = []

    sentences = split_by_sentences(text)
    lemms = []

    for sentence in sentences:
            sentence_words = split_by_words(sentence)
            lemms.append({"lemma": sentence_words[0], "register": None})

            for sentence_word in sentence_words[1:]:
                lemms.append({"lemma": sentence_word, "register": "get_register"})

    for lemma in lemms:
        word = MyWord(lemma["lemma"], tags=tags, is_normal_form=is_normal_form, word_register=lemma["register"])

        if word.parses:
            frequency = 1 / len(set([(w.normal_form, w.tag.POS) for w in word.parses]))

            if "multianim" in word.all_tags:
                frequency = frequency / 2
        else:
            frequency = 1

        lemma["frequency"] = str(frequency)

        if word.parse_chosen and "multianim" not in word.all_tags:

            dict_row = {
                "lemma": word.parse_chosen.normal_form,
                "pos": word.parse_chosen.tag.POS,
                "tags": word.required_tags + word.extra_tags,
                "frequency": lemma["frequency"],
                "source": source
            }

            if word.parse_chosen and word.parse_chosen.tag.animacy:
                dict_row["tags"].append(word.parse_chosen.tag.animacy)

            dict_row["tags"] = set(dict_row["tags"])

            if dict_row not in dict_rows:
                dict_rows.append(dict_row)

        else:
            for parse in word.parses:
                tag = str(parse.tag).replace(" ", ",").split(",")

                if "multianim" in word.all_tags:
                    tag.append("multianim")

                myword = MyWord(
                        word=parse.word,
                        tags=tag,
                        is_normal_form=True,
                        word_register=word_register
                    )
                dict_row = {
                    "lemma": parse.normal_form,
                    "pos": parse.tag.POS,
                    "tags": myword.required_tags + myword.extra_tags,
                    "frequency": lemma["frequency"],
                    "source": source
                }

                if myword.parse_chosen and myword.parse_chosen.tag.animacy:
                    dict_row["tags"].append(myword.parse_chosen.tag.animacy)

                dict_row["tags"] = set(dict_row["tags"])

                if dict_row not in dict_rows:
                    dict_rows.append(dict_row)

    for d_row in dict_rows:
        d_row["tags"] = sorted(list(d_row["tags"]))
        print(d_row)


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


add_freq_dict()
add_dict("Вася обиделся. Паша ушел к испанке", source=None)