#!/usr/bin/python
# -*- coding: utf-8 -*-


from config.config import engine
from syurbot_db.add_words import get_lexeme_dict_rows, write_words_rows


connection = engine.connect()


def get_freq_dict_rows():
    freq_dict_query = connection.execute(
        """
        SELECT * 
        FROM freq_dict
        """
    )
    rows = []

    for freq_dict_row in freq_dict_query:
        rows += get_lexeme_dict_rows(
            lexeme=freq_dict_row.lexeme,
            tags=set(freq_dict_row.tags.split(",")),
            word_register="get_register",
            is_normal_form=True,
            source_id=1,
            frequency=freq_dict_row.frequency,
            purpose="add_db_freq_dict"
        )

    return rows


def group_word_temp_rows():
    grouped_word_temp = connection.execute(
        """
        SELECT word, tagset_id, source_id, hash, sum(frequency) as frequency
        FROM syurbotdb.word_temp 
        GROUP BY hash
        ORDER BY word
    """)

    for row in grouped_word_temp:
        connection.execute(
            """
            INSERT INTO word (word, tagset_id, source_id, hash, frequency) 
            VALUES ('{}', {}, {}, '{}', {})""".format(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4]
            )
        )

    connection.execute(
        """
        TRUNCATE TABLE word_temp
        """
    )


"""
freq_dict_rows = get_freq_dict_rows()
write_words_rows(freq_dict_rows)
group_word_temp_rows()
"""
