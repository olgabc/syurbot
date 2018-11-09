from config.config import DB
import re
import os
from sqlalchemy import Table, MetaData



metadata = MetaData(DB)
sentences = Table('sentences', metadata, autoload=True)
sentences_insert = sentences.insert()


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

