#!/usr/bin/python
# # -*- coding: utf-8 -*-

from libs.text_funcs import load_some_text
from syur_classes import MyWord
from libs.text_funcs import split_by_words, split_by_sentences
from syurbot_db.add_words import get_lexeme_dict_rows, write_words_rows, group_word_temp_rows
from syurbot_db.db_models.source_dict import SourceDictModel
from config.config import engine
from syurbot_db.hashing import row_to_hash
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError as SQLProgrammingError

MyWord.purpose = "add_db_source_dict"
connection = engine.connect()


def add_source_dict(
        source_id,
        source_text=None,
        sentences=None,

):

    #SourceDictModel.__table__.create(engine)

    if not sentences:
        sentences = split_by_sentences(source_text)

    for sentence in sentences:
        sentences_lexemes = split_by_words(sentence)
        lexemes_with_registers = [{"lexeme": lexeme, "is_first": 0} for lexeme in sentences_lexemes]
        lexemes_with_registers[0]["is_first"] = 1
        sentence_dict = {
            "sentence": sentence,
            "source_id": source_id,
            "sentence_length": len(sentences_lexemes),
            "fixed_words_qty": 0,
            "trash_words_qty": 0
        }

        for lexeme in lexemes_with_registers:
            lexeme_hash = row_to_hash([lexeme["lexeme"], str(lexeme["is_first"])])
            select_lexeme_text = text(
                """
                SELECT id, hash, frequency, type FROM source_dict
                WHERE hash = :lexeme_hash
                """
            )
            select_lexeme = connection.execute(
                select_lexeme_text,
                lexeme_hash=lexeme_hash
            ).fetchone()

            if select_lexeme:
                lexeme_id = select_lexeme.id
                frequency = select_lexeme.frequency
                lexeme_type = select_lexeme.type

                update_source_dict_text = text(
                    """
                    UPDATE source_dict SET frequency = :frequency
                    WHERE id = :id
                    """
                )
                connection.execute(
                    update_source_dict_text,
                    frequency + 1,
                    lexeme_id
                )

            else:
                get_register = "get_register"

                if lexeme["is_first"]:
                    get_register = None

                lexeme_type = MyWord(word=lexeme["lexeme"], word_register=get_register).info
                insert_into_source_dict_text = text(
                    """
                    INSERT INTO source_dict (lexeme, is_first, tags, hash, type, frequency)
                    VALUES (:lexeme, :is_first, '', :lexeme_hash, :lexeme_type, 1) 
                    """

                )

                connection.execute(
                    insert_into_source_dict_text,
                    lexeme=lexeme["lexeme"],
                    is_first=lexeme["is_first"],
                    lexeme_hash=lexeme_hash,
                    lexeme_type=lexeme_type
                )

            if lexeme_type == "trash":
                sentence_dict["trash_words_qty"] += 1
            elif lexeme_type == "fixed":
                sentence_dict["fixed_words_qty"] += 1

        try:
            insert_into_sentence_text = text(
                """
                INSERT INTO sentence (sentence, source_id, sentence_length, fixed_words_qty, trash_words_qty)
                VALUES (:sentence, :source_id, :sentence_length, :fixed_words_qty, :trash_words_qty)
                """
            )
            connection.execute(
                insert_into_sentence_text,
                sentence=sentence_dict["sentence"],
                source_id=sentence_dict["source_id"],
                sentence_length=sentence_dict["sentence_length"],
                fixed_words_qty=sentence_dict["fixed_words_qty"],
                trash_words_qty=sentence_dict["trash_words_qty"],
            )
        except SQLProgrammingError:
            continue


def get_source_dict_rows(source_id):
    source_dict_query = connection.execute(
        """
        SELECT * 
        FROM source_dict
        """
    )
    rows = []

    for source_dict_row in source_dict_query:
        get_register = "get_register"
        if source_dict_row.is_first:
            get_register = None
        rows += get_lexeme_dict_rows(
            lexeme=source_dict_row.lexeme,
            tags=None,
            word_register=get_register,
            is_normal_form=False,
            source_id=source_id,
            frequency=source_dict_row.frequency,
            purpose="add_db_source_dict"
        )

    return rows


"""
mytext = load_some_text("ann_kar.txt")
add_source_dict(text=mytext, source_id=2)
source_dict_rows = get_source_dict_rows(source_id=2)
write_words_rows(source_dict_rows)
group_word_temp_rows()
"""
