import re
import os
from syurbot_db.frequency import FrequencyModel
from syurbot_db.word import WordModel
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
        SESSION.add(WordModel(word_json=json_row))
    
    SESSION.commit()
    SESSION.close()


def add_dict(text, source, tags=None, is_normal_form=False, word_register="get_register"):

    if word_register == "get_register":
        words = {}
        sentences = split_by_sentences(text)

        for sentence in sentences:
            sentence_words = split_by_words(sentence)
            words[sentence_words[0]] = None

            for word in sentence_words[1:]:
                words[word] = "get_register"

    print(words, text)
    
    unique_words = set(text.split_by_words())
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
     """
add_dict("Вася обиделся. Паша ушел", source=None)


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

