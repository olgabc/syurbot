#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os


def get_word_register(word):
    if word.islower():
        return "lower"

    elif word.istitle():
        return "title"

    elif word.isupper():
        return "upper"


def replace_word_with_case(word_f, word_r):
    if word_f.islower():
        return word_f.replace(word_f, word_r.lower())

    elif word_f.istitle():
        return word_f.replace(word_f, word_r.capitalize())

    elif word_f.isupper():
        return word_f.replace(word_f, word_r.upper())


def print_if(to_print, pattern='', word=''):
    if to_print:
        print("{}, {}".format(pattern, word))


def load_some_text(
        name,
        folder=os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
            "syurbot_db",
            "books"
        )
):
    file_path = os.path.join(
        folder,
        name
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
    text = re.sub(r'[«»]', "", text)
    text = re.sub(r'[^-A-яA-z\s\d]|(?<![A-яA-z](?=.[A-яA-z]))-', "", text)
    text = re.sub(r'(\s+)', " ", text)
    text = re.sub(r'(^\s|\s$)', "", text)
    words = text.split(" ")
    return words


def replace_word_in_sentence(word_f, word_r, sentence):
    word_r = replace_word_with_case(word_f, word_r)
    sentence = re.sub(
        r'(^|\b){}(\b|$)'.format(word_f),
        '{}'.format(replace_word_with_case(word_f, word_r)),
        sentence
    )
    return sentence