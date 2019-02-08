# -*- coding: utf-8 -*-

from syurbot_db.db_requests import get_tags_ids
import hashlib


def row_to_hash(cells_list):
    assert isinstance(cells_list, list), "cells_list must be list"
    cells_string = ",".join(cells_list)
    m = hashlib.md5()
    m.update(cells_string.encode('utf-8'))
    cells_hash = m.hexdigest()
    return cells_hash


def tagset_to_hash(tags_list):
    sorted_tags_ids = sorted(list(get_tags_ids(tags_list, format_type="str")))
    tags_string = ",".join(sorted_tags_ids)
    m = hashlib.md5()
    m.update(tags_string.encode('utf-8'))
    tagset_hash = m.hexdigest()
    return tagset_hash
