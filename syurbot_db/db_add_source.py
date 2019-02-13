#!/usr/bin/python
# # -*- coding: utf-8 -*-

from libs.text_funcs import load_some_text
from syur_classes import MyWord
from syurbot_db.db_models.sentence_temp import SentenceTempModel
from libs.text_funcs import split_by_words, split_by_sentences
#from syurbot_db.add_words import get_lexeme_dict_rows, write_words_rows
from syurbot_db.db_models.source_dict import SourceDictModel
from config.config import engine


MyWord.purpose = "add_db_source_dict"
connection = engine.connect()


def add_source_dict(
        source_id,
        text=None,
        sentences=None,

):

    SourceDictModel.__table__.create(engine)
    SentenceTempModel.__table__.create(engine)

    if not sentences:
        sentences = split_by_sentences(text)

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
            select_lexeme = connection.execute(
                """
                SELECT id, frequency, type FROM source_dict
                WHERE lexeme = '{}' AND is_first = {}
                """.format(
                    lexeme["lexeme"],
                    lexeme["is_first"]
                )
            ).fetchone()
            if select_lexeme:
                lexeme_id = select_lexeme.id
                frequency = select_lexeme.frequency + 1
                lexeme_type = select_lexeme.type

                connection.execute(
                    """
                    UPDATE source_dict SET frequency = {}
                    WHERE id = {}
                    """.format(
                        frequency,
                        lexeme_id
                    )
                )

            else:
                get_register = "get_register"

                if lexeme["is_first"]:
                    get_register = None

                lexeme_type = MyWord(word=lexeme["lexeme"], word_register=get_register).info
                connection.execute(
                    """
                    INSERT INTO source_dict (lexeme, is_first, type, frequency)
                    VALUES ('{}', '{}', '{}', {}) 
                    """.format(
                        lexeme["lexeme"],
                        lexeme["is_first"],
                        lexeme_type,
                        1
                    )
                )

            if lexeme_type == "trash":
                sentence_dict["trash_words_qty"] += 1
            elif lexeme_type == "fixed":
                sentence_dict["fixed_words_qty"] += 1

        connection.execute(
            """
            INSERT INTO sentence_temp (sentence, source_id, sentence_length, fixed_words_qty, trash_words_qty)
            VALUES ("{}", {}, {}, {}, {})
            """.format(
                sentence_dict["sentence"],
                sentence_dict["source_id"],
                sentence_dict["sentence_length"],
                sentence_dict["fixed_words_qty"],
                sentence_dict["trash_words_qty"],
            )
        )


mytext = load_some_text("ann_kar.txt")
add_source_dict(text=mytext, source_id=2)
